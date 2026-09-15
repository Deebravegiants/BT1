# [H] CVE-2020-24381

## Summary
Severity: High
Advisory: CVE-2020-24381
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-19
Source: https://osv.dev/vulnerability/CVE-2020-24381
Type: osv

## Details
GUnet Open eClass Platform (aka openeclass) before 3.11 might allow remote attackers to read students' submitted assessments because it does not ensure that the web server blocks directory listings, and the data directory is inside the web root by default.

## References
- https://emaragkos.gr/cve-2020-24381/
- https://github.com/gunet/openeclass/issues/39
