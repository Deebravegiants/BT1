# [M] CVE-2021-41571

## Summary
Severity: Medium
Advisory: CVE-2021-41571
Aliases: GHSA-3whx-qrj5-hh2h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-01
Source: https://osv.dev/vulnerability/CVE-2021-41571
Type: osv

## Details
In Apache Pulsar it is possible to access data from BookKeeper that does not belong to the topics accessible by the authenticated user. The Admin API get-message-by-id requires the user to input a topic and a ledger id. The ledger id is a pointer to the data, and it is supposed to be a valid it for the topic. Authorisation controls are performed against the topic name and there is not proper validation the that ledger id is valid in the context of such ledger. So it may happen that the user is able to read from a ledger that contains data owned by another tenant. This issue affects Apache Pulsar Apache Pulsar version 2.8.0 and prior versions; Apache Pulsar version 2.7.3 and prior versions; Apache Pulsar version 2.6.4 and prior versions.

## References
- https://lists.apache.org/thread/8n3k7pvyh4cf9q2jfzb6pb32ync6xlvr
- https://github.com/apache/pulsar/issues/11814
- https://pulsar.apache.org/admin-rest-api/#operation/getLastMessageId
