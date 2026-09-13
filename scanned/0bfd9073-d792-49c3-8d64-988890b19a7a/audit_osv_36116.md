# [C] CVE-2026-21413

## Summary
Severity: Critical
Advisory: CVE-2026-21413
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-21413
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the lossless_jpeg_load_raw functionality of LibRaw Commit 0b56545 and Commit d20315b. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-21413.json
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2331
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2331
- https://access.redhat.com/errata/RHSA-2026:11360
- https://access.redhat.com/errata/RHSA-2026:13284
- https://access.redhat.com/errata/RHSA-2026:13854
- https://access.redhat.com/errata/RHSA-2026:13860
- https://access.redhat.com/errata/RHSA-2026:13868
- https://access.redhat.com/errata/RHSA-2026:13870
- https://access.redhat.com/errata/RHSA-2026:14224
- https://access.redhat.com/errata/RHSA-2026:14655
- https://access.redhat.com/errata/RHSA-2026:14673
- https://access.redhat.com/errata/RHSA-2026:19345
- https://access.redhat.com/security/cve/CVE-2026-21413
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21413.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-21413
- https://bugzilla.redhat.com/show_bug.cgi?id=2455929
