# [C] Access of Resource Using Incompatible Type ('Type Confusion')  in yourls/yourls

## Summary
Severity: Critical
Advisory: GHSA-vf23-f26f-mjj9
CVE: CVE-2019-14537
CWE: CWE-843
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-23
Source: https://github.com/advisories/GHSA-vf23-f26f-mjj9
Type: github-advisory

## Affected
- Packagist: `yourls/yourls` — affected >=0 <1.7.4

## Details
### Impact
YOURLS through 1.7.3 is affected by a type juggling vulnerability in the API component that can result in login bypass.

### Patches
https://github.com/YOURLS/YOURLS/releases/tag/1.7.4
https://github.com/YOURLS/YOURLS/pull/2542

### References
* https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-14537
* https://github.com/Wocanilo/CVE-2019-14537

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [YOURLS repository](https://github.com/YOURLS/YOURLS)

## References
- https://github.com/YOURLS/YOURLS/security/advisories/GHSA-vf23-f26f-mjj9
- https://nvd.nist.gov/vuln/detail/CVE-2019-14537
- https://github.com/YOURLS/YOURLS/pull/2542
- https://github.com/Wocanilo/CVE-2019-14537
- https://github.com/YOURLS/YOURLS
- https://github.com/YOURLS/YOURLS/commits/master
- https://github.com/YOURLS/YOURLS/releases
- https://github.com/advisories/GHSA-vf23-f26f-mjj9
- https://security-garage.com/index.php/cves/cve-2019-14537-api-authentication-bypass-via-type-juggling
