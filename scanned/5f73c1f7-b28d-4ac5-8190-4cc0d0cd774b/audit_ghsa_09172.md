# [H] net-imap vulnerable to STARTTLS stripping via invalid response timing

## Summary
Severity: High
Advisory: GHSA-vcgp-9326-pqcp
CVE: CVE-2026-42246
CWE: CWE-392, CWE-393, CWE-636, CWE-754, CWE-841
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-vcgp-9326-pqcp
Type: github-advisory

## Affected
- RubyGems: `net-imap` — affected >=0.6.0 <0.6.4
- RubyGems: `net-imap` — affected >=0.5.0 <0.5.14
- RubyGems: `net-imap` — affected >=0.4.0 <0.4.24
- RubyGems: `net-imap` — affected >=0 <0.3.10

## Details
### Summary

A man-in-the-middle attacker can cause `Net::IMAP#starttls` to return "successfully", without starting TLS.

### Details

When using `Net::IMAP#starttls` to upgrade a plaintext connection to use TLS, a man-in-the-middle attacker can inject a tagged `OK` response with an easily predictable tag.  By sending the response before the client finishes sending the command, the command completes "successfully" before the response handler is registered.  This allows `#starttls` to return without error, but the response handler is never invoked, the TLS connection is never established, and the socket remains unencrypted.

This allows man-in-the-middle attackers to perform a STARTTLS stripping attack, unless the client code explicitly checks `Net::IMAP#tls_verified?`.

### Impact

TLS bypass, leading to cleartext transmission of sensitive information.

### Mitigation

* Upgrade to a patched version of net-imap that raises an exception whenever `#starttls` does not establish TLS.
* Connect to an implicit TLS port, rather than use `STARTTLS` with a cleartext port.
  This is strongly recommended anyway:
  * [RFC 8314](https://www.rfc-editor.org/info/rfc8314): Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access
  * [NO STARTTLS](https://nostarttls.secvuln.info/): Why TLS is better without STARTTLS, A Security Analysis of STARTTLS in the Email Context
* Explicitly verify `Net::IMAP#tls_verified?` is `true`, before using the connection after `#starttls`.

## References
- https://github.com/ruby/net-imap/security/advisories/GHSA-vcgp-9326-pqcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42246
- https://github.com/ruby/net-imap/commit/0ede4c40b1523dfeaf95777b2678e54cc0fd9618
- https://github.com/ruby/net-imap/commit/24a4e770b43230286a05aa2a9746cdbb3eb8485e
- https://github.com/ruby/net-imap/commit/97e2488fb5401a1783bddd959dde007d9fbce42c
- https://github.com/ruby/net-imap/commit/f79d35bf5833f186e81044c57c843eda30c873da
- https://github.com/ruby/net-imap
- https://github.com/ruby/net-imap/releases/tag/v0.3.10
- https://github.com/ruby/net-imap/releases/tag/v0.4.24
- https://github.com/ruby/net-imap/releases/tag/v0.5.14
- https://github.com/ruby/net-imap/releases/tag/v0.6.4
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/net-imap/CVE-2026-42246.yml
- https://nostarttls.secvuln.info
- https://www.rfc-editor.org/info/rfc8314
