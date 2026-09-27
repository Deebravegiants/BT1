# [H] Net::OAuth versions before 0.33 for Perl check HMAC-SHA1, HMAC-SHA256 and PLAINTEXT signatures with a non-constant-time comparison in verify

## Summary
Severity: High
Advisory: CVE-2026-75589
Aliases: GHSA-g8xr-69p3-gw56
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-75589
Type: osv

## Details
Net::OAuth versions before 0.33 for Perl check HMAC-SHA1, HMAC-SHA256 and PLAINTEXT signatures with a non-constant-time comparison in verify.

Each of the three compares the signature carried in the message against the locally computed one with the eq operator, which returns as soon as the two strings differ. The time taken to reject a signature varies with the length of the matching prefix. RSA-SHA1 is not affected, as it verifies through the RSA key object rather than by comparing strings.

A client that can submit messages and time the replies may recover a valid signature one byte at a time rather than searching the whole signature space. Under PLAINTEXT the value compared against is the signature key itself, so the search recovers consumer_secret and token_secret.

## References
- http://www.openwall.com/lists/oss-security/2026/08/19/3
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75589.json
- https://github.com/vurtdev/Net-OAuth/security/advisories/GHSA-g8xr-69p3-gw56
- https://metacpan.org/release/RRWO/Net-OAuth-0.33/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-75589
- https://github.com/vurtdev/Net-OAuth/commit/a1a16b58add85668ef4fcda642a486ceed098eba.patch
- https://github.com/vurtdev/Net-OAuth
