# [H] Savon::Model evaluates WSDL operation names as Ruby source

## Summary
Severity: High
Advisory: GHSA-mx5j-mp4f-g8jg
CVE: CVE-2026-53510
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-mx5j-mp4f-g8jg
Type: github-advisory

## Affected
- RubyGems: `savon` — affected >=0.9.8 <2.17.2

## Details
### Impact

`Savon::Model` generated SOAP operation methods by interpolating operation names into Ruby source passed to `module_eval`. An attacker who can control the operation names of a WSDL, can inject Ruby code that executes in the application process. This affects only the `.all_operations` class method provided by `Savon::Model` to automatically register all operations provided by the WSDL. Configuring `Savon::Model` with trusted operation names via `.operations` is safe.

### Patches

Patched in Savon 2.17.2.

Users should upgrade to 2.17.2 or later.

### Workarounds

Avoid `.all_operations` for untrusted WSDL documents. Use `.operations` with trusted operation names instead.

## References
- https://github.com/savonrb/savon/security/advisories/GHSA-mx5j-mp4f-g8jg
- https://github.com/savonrb/savon/commit/8f22eb543e7436f6247172c9be47e22792d375e9
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/savon/CVE-2026-53510.yml
- https://github.com/savonrb/savon
- https://github.com/savonrb/savon/releases/tag/v2.17.2
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-53510
