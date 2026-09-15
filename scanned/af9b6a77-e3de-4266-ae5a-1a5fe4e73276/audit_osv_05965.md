# [M] BIT-java-2026-23865

## Summary
Severity: Medium
Advisory: BIT-java-2026-23865
Aliases: BIT-java-min-2026-23865, BIT-jre-2026-23865, CVE-2026-23865
Ecosystem: Bitnami
Published: 2026-05-06
Source: https://osv.dev/vulnerability/BIT-java-2026-23865
Type: osv

## Affected
- Bitnami: `java` — affected >=26.0.0 <26.0.1

## Details
An integer overflow in the tt_var_load_item_variation_store function of the Freetype library in versions 2.13.2 and 2.13.3 may allow for an out of bounds read operation when parsing HVAR/VVAR/MVAR tables in OpenType variable fonts. This issue is fixed in version 2.14.2.

## References
- http://www.openwall.com/lists/oss-security/2026/03/03/8
- https://gitlab.com/freetype/freetype/-/commit/fc85a255849229c024c8e65f536fe1875d84841c
- https://nvd.nist.gov/vuln/detail/CVE-2026-23865
- https://sourceforge.net/projects/freetype/files/freetype2/2.14.2/
- https://www.facebook.com/security/advisories/cve-2026-23865
