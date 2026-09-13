# [H] HTTP::Tiny versions before 0.095 for Perl forward credential headers to cross-origin redirect targets

## Summary
Severity: High
Advisory: CVE-2026-7017
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-7017
Type: osv

## Details
HTTP::Tiny versions before 0.095 for Perl forward credential headers to cross-origin redirect targets.

When the server returns a 3xx redirect, `_maybe_redirect` follows the `Location:` header and `_prepare_headers_and_cb` re-merges the caller's `headers` argument into the new request, without checking whether the redirect target shares an origin with the original URL. Caller-supplied `Authorization`, `Cookie` and `Proxy-Authorization` headers are therefore re-sent to whatever host the redirect names, across scheme, host or port boundaries, and including `https` to `http` downgrades that expose them in plaintext on the wire.

The HTTP::Tiny POD note that "Authorization headers will not be included in a redirected request" applied only to the URL-userinfo Basic-auth path, not to headers passed explicitly by the caller.

## References
- http://www.openwall.com/lists/oss-security/2026/07/07/13
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7017.json
- https://metacpan.org/release/HAARG/HTTP-Tiny-0.095-TRIAL/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-7017
- https://github.com/Perl-Toolchain-Gang/HTTP-Tiny/pull/36
- https://github.com/Perl-Toolchain-Gang/HTTP-Tiny/commit/84984ef3930ddd4afcf5eb83b40d3cee200739c3.patch
- https://github.com/Perl-Toolchain-Gang/HTTP-Tiny/commit/8f32ca89e21c3ad0422adc698fa6ad17a193f55f.patch
- https://github.com/Perl-Toolchain-Gang/HTTP-Tiny/commit/e7a03aedf2395158f2b0d3bad2df943349227bb3.patch
- https://github.com/Perl-Toolchain-Gang/HTTP-Tiny
