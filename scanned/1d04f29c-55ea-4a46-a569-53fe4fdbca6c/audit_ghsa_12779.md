# [M] SimpleSAMLphp simplesamlphp-module-openid

## Summary
Severity: Medium
Advisory: GHSA-ggj9-6x8j-49w9
CVE: CVE-2010-10002
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-01
Source: https://github.com/advisories/GHSA-ggj9-6x8j-49w9
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp-module-openid` — affected >=0 <1.0

## Details
A vulnerability classified as problematic has been found in SimpleSAMLphp simplesamlphp-module-openid. Affected is an unknown function of the file `templates/consumer.php` of the component `OpenID Handler`. The manipulation of the argument `AuthState` leads to cross site scripting. It is possible to launch the attack remotely. Upgrading to version 1.0 can address this issue. The name of the patch is d652d41ccaf8c45d5707e741c0c5d82a2365a9a3. It is recommended to upgrade the affected component. VDB-217170 is the identifier assigned to this vulnerability.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-10002
- https://github.com/simplesamlphp/simplesamlphp-module-openid/commit/d652d41ccaf8c45d5707e741c0c5d82a2365a9a3
- https://github.com/simplesamlphp/simplesamlphp-module-openid
- https://github.com/simplesamlphp/simplesamlphp-module-openid/releases/tag/v1.0
- https://vuldb.com/?ctiid.217170
- https://vuldb.com/?id.217170
