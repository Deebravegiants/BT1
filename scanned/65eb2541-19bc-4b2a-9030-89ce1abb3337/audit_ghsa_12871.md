# [M] simplesamlphp-module-openidprovider Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-chgc-rqjr-46gg
CVE: CVE-2010-10008
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-17
Source: https://github.com/advisories/GHSA-chgc-rqjr-46gg
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp-module-openidprovider` — affected >=0 <0.9.0

## Details
A vulnerability was found in simplesamlphp simplesamlphp-module-openidprovider up to 0.8.x. It has been declared as problematic. Affected by this vulnerability is an unknown functionality of the file templates/trust.tpl.php. The manipulation of the argument StateID leads to cross site scripting. The attack can be launched remotely. Upgrading to version 0.9.0 is able to address this issue. The name of the patch is 8365d48c863cf06ccf1465cc0a161cefae29d69d. It is recommended to upgrade the affected component. The identifier VDB-218473 was assigned to this vulnerability. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-10008
- https://github.com/simplesamlphp/simplesamlphp-module-openidprovider/commit/8365d48c863cf06ccf1465cc0a161cefae29d69d
- https://github.com/simplesamlphp/simplesamlphp-module-openidprovider
- https://github.com/simplesamlphp/simplesamlphp-module-openidprovider/releases/tag/v0.9.0
- https://vuldb.com/?ctiid.218473
- https://vuldb.com/?id.218473
