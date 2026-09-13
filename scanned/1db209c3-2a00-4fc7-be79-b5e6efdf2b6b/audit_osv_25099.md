# [C] CVE-2023-30769

## Summary
Severity: Critical
Advisory: CVE-2023-30769
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-17
Source: https://osv.dev/vulnerability/CVE-2023-30769
Type: osv

## Details
Vulnerability discovered is related to the peer-to-peer (p2p) communications, attackers can craft consensus messages, send it to individual nodes and take them offline. An attacker can crawl the network peers using getaddr message and attack the unpatched nodes.

## References
- https://www.halborn.com/blog/post/halborn-discovers-zero-day-impacting-dogecoin-and-280-networks
- https://www.halborn.com/disclosures
