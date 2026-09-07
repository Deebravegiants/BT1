# [M] ImpressCMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-667r-p4gg-7m2q
CVE: CVE-2023-37785
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-13
Source: https://github.com/advisories/GHSA-667r-p4gg-7m2q
Type: github-advisory

## Affected
- Packagist: `impresscms/impresscms` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in ImpressCMS v1.4.5 and before allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the `smile_code` parameter of the component `/editprofile.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37785
- https://github.com/CrownZTX/cve-description
- https://github.com/ImpressCMS/impresscms
