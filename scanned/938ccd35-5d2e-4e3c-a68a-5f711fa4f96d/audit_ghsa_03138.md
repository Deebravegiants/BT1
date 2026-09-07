# [M] Cross-site scripting in ThinkAdmin

## Summary
Severity: Medium
Advisory: GHSA-v47f-vp3p-5j6h
CVE: CVE-2020-29315
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-v47f-vp3p-5j6h
Type: github-advisory

## Affected
- Packagist: `zoujingli/thinkadmin` — affected >=0 <6.0.22

## Details
ThinkAdmin version v6 has a stored XSS vulnerability which allows remote attackers to inject an arbitrary web script or HTML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29315
- https://github.com/zoujingli/ThinkAdmin/issues/255
- https://github.com/zoujingli/ThinkAdmin/commit/5e7c2325008d0191f941666b5589c08a070ce838
- https://github.com/zoujingli/ThinkAdmin
