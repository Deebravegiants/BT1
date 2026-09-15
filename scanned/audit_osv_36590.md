# [H] CVE-2026-24660

## Summary
Severity: High
Advisory: CVE-2026-24660
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-24660
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the x3f_load_huffman functionality of LibRaw Commit d20315b. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24660.json
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2359
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2359
- https://access.redhat.com/errata/RHSA-2026:13284
- https://access.redhat.com/errata/RHSA-2026:15924
- https://access.redhat.com/errata/RHSA-2026:15925
- https://access.redhat.com/errata/RHSA-2026:15926
- https://access.redhat.com/security/cve/CVE-2026-24660
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24660.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24660
- https://bugzilla.redhat.com/show_bug.cgi?id=2455926
