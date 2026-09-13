# [H] league/oauth2-server key exposed in exception message when passing as a string and providing an invalid pass phrase

## Summary
Severity: High
Advisory: GHSA-wj7q-gjg8-3cpm
CVE: CVE-2023-37260
CWE: CWE-200, CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-wj7q-gjg8-3cpm
Type: github-advisory

## Affected
- Packagist: `league/oauth2-server` — affected >=8.3.2 <8.4.2
- Packagist: `league/oauth2-server` — affected >=8.5.0 <8.5.3

## Details
### Impact
Servers that passed their keys to the CryptKey constructor as as string instead of a file path will have had that key included in a LogicException message if they did not provide a valid pass phrase for the key where required. 

### Patches
This issue has been patched so that the provided key is no longer exposed in the exception message in the scenario outlined above. Users should upgrade to version 8.5.3 or 8.4.2 to receive the patch.

### Workarounds
We recommend upgrading the oauth2-server to one of the patched releases (8.5.3 or 8.4.2). If you are unable to upgrade you can avoid this security issue by passing your key as a file instead of a string.

### References
* [Fix for 8.4.x](https://github.com/thephpleague/oauth2-server/pull/1359)
* [Fix for 8.5.x](https://github.com/thephpleague/oauth2-server/pull/1353)

## References
- https://github.com/thephpleague/oauth2-server/security/advisories/GHSA-wj7q-gjg8-3cpm
- https://nvd.nist.gov/vuln/detail/CVE-2023-37260
- https://github.com/thephpleague/oauth2-server/pull/1353
- https://github.com/thephpleague/oauth2-server/pull/1359
- https://github.com/thephpleague/oauth2-server
- https://github.com/thephpleague/oauth2-server/releases/tag/8.5.3
