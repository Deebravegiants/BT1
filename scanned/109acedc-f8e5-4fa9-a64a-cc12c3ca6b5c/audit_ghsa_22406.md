# [C] eZ Publish Kernel and Legacy Unrestricted Upload of File with Dangerous Type

## Summary
Severity: Critical
Advisory: GHSA-54p5-gxq6-j98g
CVE: CVE-2020-10806
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-54p5-gxq6-j98g
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-kernel` — affected >=0 <5.4.14.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=0 <5.4.14.1
- Packagist: `ezsystems/ezpublish-kernel` — affected >=6.0 <6.13.6.2
- Packagist: `ezsystems/ezpublish-kernel` — affected >=7.0 <7.5.6.2
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2017 <2017.12.7.2
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2019 <2019.03.4.2

## Details
eZ Publish Kernel before 5.4.14.1, 6.x before 6.13.6.2, and 7.x before 7.5.6.2 and eZ Publish Legacy before 5.4.14.1, 2017 before 2017.12.7.2, and 2019 before 2019.03.4.2 allow remote attackers to execute arbitrary code by uploading PHP code, unless the vhost configuration permits only app.php execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10806
- https://ezplatform.com/security-advisories/ezsa-2020-001-remote-code-execution-in-file-uploads
