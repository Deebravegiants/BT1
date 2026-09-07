# [M] Cross-site scripting (XSS) vulnerability in CakePHP

## Summary
Severity: Medium
Advisory: GHSA-vc29-mvwv-wpcq
CVE: CVE-2006-4067
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-vc29-mvwv-wpcq
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=1.0.1.2708 <1.1.7.3363

## Details
Cross-site scripting (XSS) vulnerability in cake/libs/error.php in CakePHP before 1.1.7.3363 allows remote attackers to inject arbitrary web script or HTML via the URL, which is reflected back in a 404 (\"Not Found\") error page. NOTE: some of these details are obtained from third party information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-4067
- https://exchange.xforce.ibmcloud.com/vulnerabilities/28256
- https://github.com/cakephp/cakephp
