# [M] CVE-2022-45195

## Summary
Severity: Medium
Advisory: CVE-2022-45195
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-11-12
Source: https://osv.dev/vulnerability/CVE-2022-45195
Type: osv

## Details
SimpleXMQ before 3.4.0, as used in SimpleX Chat before 4.2, does not apply a key derivation function to intended data, which can interfere with forward secrecy and can have other impacts if there is a compromise of a single private key. This occurs in the X3DH key exchange for the double ratchet protocol.

## References
- https://github.com/simplex-chat/simplexmq/compare/v3.3.0...v3.4.0
- https://github.com/trailofbits/publications/blob/master/reviews/SimpleXChat.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45195.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-45195
- https://github.com/simplex-chat/simplexmq/pull/548
- https://simplex.chat/blog/20221108-simplex-chat-v4.2-security-audit-new-website.html
