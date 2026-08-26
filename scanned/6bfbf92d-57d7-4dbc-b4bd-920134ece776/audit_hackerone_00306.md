# [H] CVE-2019-5736: Escape from Docker and Kubernetes containers to root on host

## Summary
Severity: High (CVSS 8.6)
Program: Internet Bug Bounty
Weakness: Privilege Escalation
Reporter: adam_iwaniuk
State: resolved
Disclosed: 2019-09-26T20:35:06.848Z
CVE: CVE-2019-5736
Source: https://hackerone.com/reports/495495

## Details
description here: 
https://blog.dragonsector.pl/2019/02/cve-2019-5736-escape-from-docker-and.html
PoC: https://github.com/q3k/cve-2019-5736-poc

Some more links:
https://seclists.org/oss-sec/2019/q1/119
https://access.redhat.com/security/cve/cve-2019-5736

## Impact

It allows to escape from container to root on host when unpatched version of Docker and Kubernetes are used.
This affects a pretty big part of internet, since a lot of services are using Docker and Kubernets these days.
It has also serious impact on cloud services
AWS https://aws.amazon.com/security/security-bulletins/AWS-2019-002/ and GCP https://cloud.google.com/kubernetes-engine/docs/security-bulletins#february-11-2019-runc
https://kubernetes.io/blog/2019/02/11/runc-and-cve-2019-5736/
