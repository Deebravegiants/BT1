# [C] Net::OAuth versions before 0.33 for Perl allow the sender to choose the signature algorithm in verify

## Summary
Severity: Critical
Advisory: CVE-2026-72889
Aliases: GHSA-c8rm-g5cm-4pf5
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-72889
Type: osv

## Details
Net::OAuth versions before 0.33 for Perl allow the sender to choose the signature algorithm in verify.

verify resolves the signature method class from the signature_method parameter of the incoming message. signature_method is required on every request, so the algorithm used to check a signature is chosen by whoever sent it, and nothing lets the verifying party pin the method instead. When a message names HMAC-SHA1 or HMAC-SHA256, the key is derived from consumer_secret and token_secret rather than from the key the provider deployed.

A provider deployed on RSA-SHA1 holds only the consumer public key, and RFC 5849 does not use consumer_secret for that method, so the required parameter is filled with a placeholder. A client that names HMAC-SHA1 instead has its signature checked against that placeholder, so a guessable one is enough to forge requests for any consumer key and token.

## References
- http://www.openwall.com/lists/oss-security/2026/08/19/2
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72889.json
- https://github.com/vurtdev/Net-OAuth/security/advisories/GHSA-c8rm-g5cm-4pf5
- https://metacpan.org/release/RRWO/Net-OAuth-0.33/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-72889
- https://github.com/vurtdev/Net-OAuth/commit/c467adf45c8d77ac4b92ad78b3eebf949252ba7f.patch
- https://github.com/vurtdev/Net-OAuth
- https://datatracker.ietf.org/doc/html/rfc5849#section-3.4.2
- https://datatracker.ietf.org/doc/html/rfc5849#section-3.4.3
