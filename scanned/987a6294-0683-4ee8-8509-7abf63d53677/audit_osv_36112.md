# [C] CVE-2026-20911

## Summary
Severity: Critical
Advisory: CVE-2026-20911
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-20911
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the HuffTable::initval functionality of LibRaw Commit 0b56545 and Commit d20315b. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-20911.json
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2330
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2330
- https://access.redhat.com/security/cve/CVE-2026-20911
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/20xxx/CVE-2026-20911.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-20911
- https://bugzilla.redhat.com/show_bug.cgi?id=2455959
