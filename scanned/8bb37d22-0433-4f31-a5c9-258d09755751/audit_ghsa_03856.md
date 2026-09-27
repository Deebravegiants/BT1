# [M] Missing Authentication for Critical Function in LibreNMS

## Summary
Severity: Medium
Advisory: GHSA-277v-gwfr-hmpj
CVE: CVE-2019-10668
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-277v-gwfr-hmpj
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.50.1

## Details
An issue was discovered in LibreNMS through 1.47. A number of scripts import the Authentication libraries, but do not enforce an actual authentication check. Several of these scripts disclose information or expose functions that are of a sensitive nature and are not expected to be publicly accessible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10668
- https://www.darkmatter.ae/xen1thlabs/librenms-authentication-bypass-vulnerability-xl-19-016
