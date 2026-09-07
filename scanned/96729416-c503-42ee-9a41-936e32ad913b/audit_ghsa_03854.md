# [M] Exposure of Sensitive Information to an Unauthorized Actor in LibreNMS

## Summary
Severity: Medium
Advisory: GHSA-f4hh-xxqh-wgpq
CVE: CVE-2019-10667
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-f4hh-xxqh-wgpq
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.50.1

## Details
An issue was discovered in LibreNMS through 1.47. Information disclosure can occur: an attacker can fingerprint the exact code version installed and disclose local file paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10667
- https://www.darkmatter.ae/xen1thlabs/librenms-information-disclosure-vulnerability-xl-19-018
