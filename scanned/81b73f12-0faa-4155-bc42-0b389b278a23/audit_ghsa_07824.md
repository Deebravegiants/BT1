# [M] Nokogiri does not check the return value from xmlC14NExecute

## Summary
Severity: Medium
Advisory: GHSA-wx95-c6cv-8532
CVE: CVE-2026-79772
CWE: CWE-252
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-wx95-c6cv-8532
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=1.5.1 <1.19.1

## Details
## Summary

Nokogiri's CRuby extension fails to check the return value from `xmlC14NExecute` in the method `Nokogiri::XML::Document#canonicalize` and `Nokogiri::XML::Node#canonicalize`. When canonicalization fails, an empty string is returned instead of raising an exception. This incorrect return value may allow downstream libraries to accept invalid or incomplete canonicalized XML, which has been demonstrated to enable signature validation bypass in SAML libraries.

JRuby is not affected, as the Java implementation correctly raises `RuntimeError` on canonicalization failure.

## Mitigation

Upgrade to Nokogiri `>= 1.19.1`.

## Severity

The maintainers have assessed this as **Medium** severity. Nokogiri itself is a parsing library without a clear security boundary related to canonicalization, so the direct impact is that a method returns incorrect data on invalid input. However, this behavior was exploited in practice to bypass SAML signature validation in downstream libraries (see References).

## Credit

This vulnerability was responsibly reported by HackerOne researcher `d4d`.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-wx95-c6cv-8532
- https://nvd.nist.gov/vuln/detail/CVE-2026-79772
- https://github.com/sparklemotion/nokogiri
- https://www.vulncheck.com/advisories/nokogiri-before-unchecked-return-value-canonicalize
