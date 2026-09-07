# [M] LeafKit allows XSS with untrusted user input

## Summary
Severity: Medium
Advisory: GHSA-rv3x-xq3r-8j9h
CVE: CVE-2021-37634
CWE: CWE-79, CWE-80
Ecosystem: SwiftURL
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-rv3x-xq3r-8j9h
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/leaf-kit` — affected >=0 <1.3.0

## Details
### Impact
This affects anyone passing unsanitised data to Leaf's variable tags. Before this fix, Leaf would not escape any strings passed to tags as variables. If an attacker managed to find a variable that was rendered with their unsanitised data, they could inject scripts into a generated Leaf page, which could enable XSS attacks if other mitigations such as a Content Security Policy were not enabled.

### Patches
This has been patched in 1.3.0

### Workarounds
Sanitise any untrusted input before passing it to Leaf and enable a CSP to block inline script and CSS data.

### References
https://github.com/vapor/leaf-kit-ghsa-rv3x-xq3r-8j9h/pull/1

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Leaf Kit](https://github.com/vapor/leaf-kit)
* Email us at [security@vapor.codes](mailto:security@vapor.codes)

## References
- https://github.com/vapor/leaf-kit/security/advisories/GHSA-rv3x-xq3r-8j9h
- https://nvd.nist.gov/vuln/detail/CVE-2021-37634
- https://github.com/vapor/leaf-kit
- https://github.com/vapor/leaf-kit/releases/tag/1.3.0
