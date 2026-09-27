# [M] Dompdf before v2.0.0 vulnerable to chroot check bypass

## Summary
Severity: Medium
Advisory: GHSA-5qj8-6xxj-hp9h
CVE: CVE-2022-2400
CWE: CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-19
Source: https://github.com/advisories/GHSA-5qj8-6xxj-hp9h
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <2.0.0

## Details
Dompdf prior to version 2.0.0 is vulnerable to a chroot check bypass, which could cause disclosure of png and jpeg files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2400
- https://github.com/dompdf/dompdf/commit/99aeec1efec9213e87098d42eb09439e7ee0bb6a
- https://github.com/dompdf/dompdf
- https://huntr.dev/bounties/a6da5e5e-86be-499a-a3c3-2950f749202a
- https://lists.debian.org/debian-lts-announce/2023/07/msg00017.html
