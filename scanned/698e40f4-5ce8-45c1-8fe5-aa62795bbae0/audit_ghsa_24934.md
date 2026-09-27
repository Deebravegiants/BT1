# [H] SQL Injection in Zenario 7.1-7.6

## Summary
Severity: High
Advisory: GHSA-jf5f-h3wr-j666
CVE: CVE-2018-5960
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jf5f-h3wr-j666
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=7.1

## Details
Zenario v7.1 - v7.6 has SQL injection via the `Name` input field of organizer.php or admin_boxes.ajax.php in the `Categories - Edit` module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5960
- https://www.vulnerability-lab.com/get_content.php?id=2043
