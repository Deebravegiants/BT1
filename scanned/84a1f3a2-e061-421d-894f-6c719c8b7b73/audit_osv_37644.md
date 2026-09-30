# [C] Command Injection and Docker container escape allows root on host machine

## Summary
Severity: Critical
Advisory: CVE-2026-32311
Aliases: GHSA-9g44-8xv2-f2m9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-32311
Type: osv

## Details
Flowsint is an open-source OSINT graph exploration tool designed for cybersecurity investigation, transparency, and verification. Flowsint allows a user to create investigations, which are used to manage sketches and analyses. Sketches have controllable graphs, which are comprised of nodes and relationships. The sketches contain information on an OSINT target (usernames, websites, etc) within these nodes and relationships. The nodes can have automated processes execute on them called 'transformers'. A remote attacker can create a sketch, then trigger the 'org_to_asn' transform on an organization node to execute arbitrary OS commands as root on the host machine via shell metacharacters and a docker container escape. Commit b52cbbb904c8013b74308d58af88bc7dbb1b055c appears to remove the code that causes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32311.json
- https://github.com/reconurge/flowsint/security/advisories/GHSA-9g44-8xv2-f2m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32311
- https://github.com/reconurge/flowsint/commit/b52cbbb904c8013b74308d58af88bc7dbb1b055c
