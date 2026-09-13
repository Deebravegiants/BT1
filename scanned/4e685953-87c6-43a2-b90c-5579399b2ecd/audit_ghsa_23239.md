# [H] Bottle does not properly limit content-types

## Summary
Severity: High
Advisory: GHSA-873q-wpqr-xfgw
CVE: CVE-2014-3137
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-873q-wpqr-xfgw
Type: github-advisory

## Affected
- PyPI: `bottle` — affected >=0.10.0 <0.10.12
- PyPI: `bottle` — affected >=0.11.0 <0.11.7
- PyPI: `bottle` — affected >=0.12.0 <0.12.6

## Details
Bottle 0.10.x before 0.10.12, 0.11.x before 0.11.7, and 0.12.x before 0.12.6 does not properly limit content types, which allows remote attackers to bypass intended access restrictions via an accepted Content-Type followed by a `;` (semi-colon) and a Content-Type that would not be accepted, as demonstrated in YouCompleteMe to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3137
- https://github.com/bottlepy/bottle/issues/616
- https://github.com/defnull/bottle/issues/616
- https://bugzilla.redhat.com/show_bug.cgi?id=1093255
- https://github.com/bottlepy/bottle
- https://github.com/pypa/advisory-database/tree/main/vulns/bottle/PYSEC-2014-77.yaml
- http://www.debian.org/security/2014/dsa-2948
- http://www.openwall.com/lists/oss-security/2014/05/01/15
