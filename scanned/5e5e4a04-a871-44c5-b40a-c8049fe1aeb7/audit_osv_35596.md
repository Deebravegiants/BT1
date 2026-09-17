# [H] CVE-2026-10846

## Summary
Severity: High
Advisory: CVE-2026-10846
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-10846
Type: osv

## Details
NLnet Labs ldns 1.2.0 up to and including versions 1.9.0, when used in applications as (stub) resolver over UDP, lacks matching the query destination address and port with the response source address and port. Furthermore not the query ID, neither the question of the query is matched with that of the response. This makes applications, that use ldns for (stub) resolver functionality over UDP, vulnerable for off-path poisoning attacks. The drill tool, which is shipped with ldns, suffers from this vulnerability.

## References
- https://www.nlnetlabs.nl/downloads/ldns/CVE-2026-10846.txt
- http://www.openwall.com/lists/oss-security/2026/06/10/2
