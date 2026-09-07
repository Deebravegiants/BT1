# [H] Moodle SSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-vjxx-54vw-q59f
CVE: CVE-2019-6970
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vjxx-54vw-q59f
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.4

## Details
The `edit_blog.php` script allows a registered user to add external RSS feed resources. It was identified that this feature could be abused to be used as a SSRF attack vector by adding a malicious URL/TCP PORT in order to target internal network or an internet hosted server, bypassing firewall rules, IP filtering and more.

This kind of vulnerability is then called “blind” because of no response available on Moodle web site, enforcing attacker to exploit it using a “time based” approach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6970
- https://cds.thalesgroup.com/en/tcs-cert/CVE-2019-6970
- https://excellium-services.com/cert-xlm-advisory/cve-2019-6970
- https://github.com/moodle/moodle
- https://www.excellium-services.com/cert-xlm-advisory
- https://www.excellium-services.com/cert-xlm-advisory/cve-2019-6970
