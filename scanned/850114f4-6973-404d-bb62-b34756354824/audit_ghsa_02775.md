# [H] Regular Expression Denial of Service in Addressable templates

## Summary
Severity: High
Advisory: GHSA-jxhc-q857-3j6g
CVE: CVE-2021-32740
CWE: CWE-1333, CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-12
Source: https://github.com/advisories/GHSA-jxhc-q857-3j6g
Type: github-advisory

## Affected
- RubyGems: `addressable` — affected >=2.3.0 <2.8.0

## Details
### Impact

Within the URI template implementation in Addressable, a maliciously crafted template may result in uncontrolled resource consumption, leading to denial of service when matched against a URI. In typical usage, templates would not normally be read from untrusted user input, but nonetheless, no previous security advisory for Addressable has cautioned against doing this. Users of the parsing capabilities in Addressable but not the URI template capabilities are unaffected.

### Patches

The vulnerability was introduced in version 2.3.0 (previously yanked) and has been present in all subsequent versions up to, and including, 2.7.0. It is fixed in version 2.8.0.

### Workarounds

The vulnerability can be avoided by only creating Template objects from trusted sources that have been validated not to produce catastrophic backtracking.

### References

- https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
- https://cwe.mitre.org/data/definitions/1333.html
- https://www.regular-expressions.info/catastrophic.html

### For more information
If you have any questions or comments about this advisory:
* [Open an issue](https://github.com/sporkmonger/addressable/issues)

## References
- https://github.com/sporkmonger/addressable/security/advisories/GHSA-jxhc-q857-3j6g
- https://nvd.nist.gov/vuln/detail/CVE-2021-32740
- https://github.com/sporkmonger/addressable/commit/0d8a3127e35886ce9284810a7f2438bff6b43cbc
- https://github.com/sporkmonger/addressable/commit/89c76130ce255c601f642a018cb5fb5a80e679a7
- https://github.com/sporkmonger/addressable/commit/92685096b1f7235ed8986c03ce30a24972eed848#diff-fb36d3dc67e6565ffde17e666a98697f48e76dac38fabf1bb9e97cdf3b583d76
- https://github.com/advisories/GHSA-jxhc-q857-3j6g
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/addressable/CVE-2021-32740.yml
- https://github.com/sporkmonger/addressable
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SDFQM2NHNAZ3NNUQZEJTYECYZYXV4UDS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WYPVOOQU7UB277UUERJMCNQLRCXRCIQ5
