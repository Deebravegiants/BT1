# [M] xhtml2pdf Denial of Service via crafted string

## Summary
Severity: Medium
Advisory: GHSA-jj5c-hhrg-vv5h
CVE: CVE-2024-25885
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-jj5c-hhrg-vv5h
Type: github-advisory

## Affected
- PyPI: `xhtml2pdf` — affected >=0

## Details
An issue in the getcolor function in utils.py of xhtml2pdf v0.2.13 allows attackers to cause a Regular expression Denial of Service (ReDOS) via supplying a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25885
- https://gist.github.com/salvatore-abello/c88dd0027496774023ef36c7b576d206
- https://github.com/xhtml2pdf/xhtml2pdf
