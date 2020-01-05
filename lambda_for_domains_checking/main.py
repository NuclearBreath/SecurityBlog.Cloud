import multiprocessing
import boto3
import dns.resolver
import json
import os


def resolve(child_conn, domains):
    records = []
    dns_resolver = dns.resolver.Resolver()
    dns_resolver.timeout = 5
    dns_resolver.lifetime = 5
    dns_resolver.nameservers = [srv for srv in os.environ['dns_servers'].split(',')]
    for domain in domains:
        record = {}
        try:
            ns = dns_resolver.query(domain, 'NS')
            record['NS'] = str(ns.response)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout, dns.resolver.NoAnswer):
            pass
        else:
            try:
                a = dns_resolver.query(domain, 'A')
                record['A'] = str(a.response)
            except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer):
                pass
            try:
                aaaa = dns_resolver.query(domain, 'AAAA')
                record['AAAA'] = str(aaaa.response)
            except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer):
                pass
            try:
                mx = dns_resolver.query(domain, 'MX')
                record['MX'] = str(mx.response)
            except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer):
                pass
        if record:
            records.append(record)
    child_conn.send(records)
    child_conn.close()


def read_domain_list():
    domains_file_name = os.environ['domain_list']
    with open(domains_file_name, 'r') as file:
        for line in file:
            if line:
                try:
                    yield line[:-1]
                except ValueError:
                    continue


def sns_output(results):
    sns = boto3.client('sns')
    topic = os.environ['sns_topic']
    for result in results:
        response = sns.publish(
            TopicArn=topic,
            Message=json.dumps(result)
        )


def handler():
    batch_size = 500
    batch = []
    results = []
    parent_connections = []
    processes = []
    for domain in read_domain_list():
        batch.append(domain)
        if len(batch) == batch_size:
            parent_conn, child_conn = multiprocessing.Pipe()
            parent_connections.append(parent_conn)
            process = multiprocessing.Process(target=resolve, args=(child_conn, batch,))
            processes.append(process)
            batch = []
    if batch:
        parent_conn, child_conn = multiprocessing.Pipe()
        parent_connections.append(parent_conn)
        process = multiprocessing.Process(target=resolve, args=(child_conn, batch,))
        processes.append(process)
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    for conn in parent_connections:
        data = conn.recv()
        if data:
            results += data
    sns_output(results)
