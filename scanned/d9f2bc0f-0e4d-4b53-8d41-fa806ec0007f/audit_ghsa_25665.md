# [H] Denial of Service (DoS) in Nokogiri on JRuby

## Summary
Severity: High
Advisory: GHSA-gx8x-g87m-h5q6
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-11
Source: https://github.com/advisories/GHSA-gx8x-g87m-h5q6
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.13.4

## Details
## Summary

Nokogiri `v1.13.4` updates the vendored `org.cyberneko.html` library to `1.9.22.noko2` which addresses [CVE-2022-24839](https://github.com/sparklemotion/nekohtml/security/advisories/GHSA-9849-p7jc-9rmv). That CVE is rated 7.5 (High Severity).

See [GHSA-9849-p7jc-9rmv](https://github.com/sparklemotion/nekohtml/security/advisories/GHSA-9849-p7jc-9rmv) for more information.

Please note that this advisory only applies to the **JRuby** implementation of Nokogiri `< 1.13.4`.


## Mitigation

Upgrade to Nokogiri `>= 1.13.4`.


## Impact

### [CVE-2022-24839](https://github.com/sparklemotion/nekohtml/security/advisories/GHSA-9849-p7jc-9rmv) in nekohtml

- **Severity**: High 7.5
- **Type**: [CWE-400](https://cwe.mitre.org/data/definitions/400.html) Uncontrolled Resource Consumption
- **Description**: The fork of `org.cyberneko.html` used by Nokogiri (Rubygem) raises a `java.lang.OutOfMemoryError` exception when parsing ill-formed HTML markup.
- **See also**: [GHSA-9849-p7jc-9rmv](https://github.com/sparklemotion/nekohtml/security/advisories/GHSA-9849-p7jc-9rmv)

## References
- https://github.com/sparklemotion/nekohtml/security/advisories/GHSA-9849-p7jc-9rmv
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-gx8x-g87m-h5q6
- https://nvd.nist.gov/vuln/detail/CVE-2022-24839
- https://github.com/sparklemotion/nekohtml/commit/a800fce3b079def130ed42a408ff1d09f89e773d
- https://github.com/sparklemotion/nokogiri
- https://github.com/sparklemotion/nokogiri/releases/tag/v1.13.4
- https://groups.google.com/g/ruby-security-ann/c/vX7qSjsvWis/m/TJWN4oOKBwAJ?utm_medium=email&utm_source=footer
