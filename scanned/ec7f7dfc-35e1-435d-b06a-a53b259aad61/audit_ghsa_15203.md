# [M] Vapor contains an integer overflow in URI leading to potential host spoofing

## Summary
Severity: Medium
Advisory: GHSA-r6r4-5pr8-gjcp
CVE: CVE-2024-21631
CWE: CWE-1104, CWE-190
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-r6r4-5pr8-gjcp
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/vapor` — affected >=0 <4.90.0

## Details
Vapor's `vapor_urlparser_parse` function uses `uint16_t` indexes when parsing a URI's components, which may cause integer overflows when parsing untrusted inputs.

This vulnerability does not affect Vapor directly but could impact applications relying on the URI type for validating user input. 

The URI type is used in several places in Vapor. A developer may decide to use URI to represent a URL in their application (especially if that URL is then passed to the HTTP Client) and rely on its public properties and methods. However, URI may fail to properly parse a valid (albeit abnormally long) URL, due to string ranges being converted to 16-bit integers. An attacker may use this behaviour to trick the application into accepting a URL to an untrusted destination.

By padding the port number with zeros, an attacker can cause an integer overflow to occur when the URL authority is parsed and, as a result, spoof the host.

### Impact
Users attempting to treat untrusted input as a URI are vulnerable to a host spoofing attack due to an integer overflow.

### Workarounds
Validate user input before parsing as a URI or, if possible, use Foundation's `URL` and `URLComponents` utilities.

## References
- https://github.com/vapor/vapor/security/advisories/GHSA-r6r4-5pr8-gjcp
- https://nvd.nist.gov/vuln/detail/CVE-2024-21631
- https://github.com/vapor/vapor/commit/6db3d917b5ce5024a84eb265ef65691383305d70
- https://github.com/vapor/vapor
