# [M] An integer overflow in the `tt_var_load_item_variation_store` function of the Freetype library in...

## Summary
Severity: Medium
Advisory: JLSEC-2026-461
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-461
Type: osv

## Affected
- Julia: `FreeType2_jll` — affected >=2.13.2+0 <2.14.3+0

## Details
An integer overflow in the `tt_var_load_item_variation_store` function of the Freetype library in versions 2.13.2 and 2.13.3 may allow for an out of bounds read operation when parsing HVAR/VVAR/MVAR tables in OpenType variable fonts. This issue is fixed in version 2.14.2.

## References
- http://www.openwall.com/lists/oss-security/2026/03/03/8
- https://github.com/advisories/GHSA-878v-mxg6-vj8f
- https://gitlab.com/freetype/freetype/-/commit/fc85a255849229c024c8e65f536fe1875d84841c
- https://nvd.nist.gov/vuln/detail/CVE-2026-23865
- https://sourceforge.net/projects/freetype/files/freetype2/2.14.2
- https://sourceforge.net/projects/freetype/files/freetype2/2.14.2/
- https://www.facebook.com/security/advisories/cve-2026-23865
