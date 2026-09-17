# [C] A heap-based buffer overflow vulnerability exists in the HuffTable::initval functionality of...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1114
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1114
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0.22.1+0 <0.22.2+0

## Details
A heap-based buffer overflow vulnerability exists in the HuffTable::initval functionality of LibRaw Commit 0b56545 and Commit d20315b. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://access.redhat.com/security/cve/CVE-2026-20911
- https://bugzilla.redhat.com/show_bug.cgi?id=2455959
- https://github.com/advisories/GHSA-rc49-6x7v-hf76
- https://nvd.nist.gov/vuln/detail/CVE-2026-20911
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-20911.json
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2330
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2330
