# [C] A heap-based buffer overflow vulnerability exists in the lossless_jpeg_load_raw functionality of...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1115
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1115
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0.22.1+0 <0.22.2+0

## Details
A heap-based buffer overflow vulnerability exists in the `lossless_jpeg_load_raw` functionality of LibRaw Commit 0b56545 and Commit d20315b. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
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
- https://bugzilla.redhat.com/show_bug.cgi?id=2455929
- https://github.com/advisories/GHSA-g53g-r75r-95g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-21413
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-21413.json
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2331
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2331
