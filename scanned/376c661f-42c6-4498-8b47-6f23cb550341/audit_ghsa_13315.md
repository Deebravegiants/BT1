# [H] Removal of e-Tugra root certificate

## Summary
Severity: High
Advisory: GHSA-xqr8-7jwr-rhp7
CVE: CVE-2023-37920
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-xqr8-7jwr-rhp7
Type: github-advisory

## Affected
- PyPI: `certifi` — affected >=2015.4.28 <2023.7.22

## Details
Certifi 2023.07.22 removes root certificates from "e-Tugra" from the root store. These are in the process of being removed from Mozilla's trust store.

 e-Tugra's root certificates are being removed pursuant to an investigation prompted by reporting of security issues in their systems. Conclusions of Mozilla's investigation can be found [here](https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/C-HrP1SEq1A).

## References
- https://github.com/certifi/python-certifi/security/advisories/GHSA-xqr8-7jwr-rhp7
- https://nvd.nist.gov/vuln/detail/CVE-2023-37920
- https://github.com/certifi/python-certifi/commit/8fb96ed81f71e7097ed11bc4d9b19afd7ea5c909
- https://github.com/certifi/python-certifi
- https://github.com/pypa/advisory-database/tree/main/vulns/certifi/PYSEC-2023-135.yaml
- https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/C-HrP1SEq1A
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5EX6NG7WUFNUKGFHLM35KHHU3GAKXRTG
- https://security.netapp.com/advisory/ntap-20240912-0002
