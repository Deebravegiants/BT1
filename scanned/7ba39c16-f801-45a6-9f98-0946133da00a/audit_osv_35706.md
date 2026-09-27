# [H] OIDC::Lite versions through 0.12.1 for Perl allow ID Token signature verification bypass via a token-controlled algorithm allowlist in verify

## Summary
Severity: High
Advisory: CVE-2026-13089
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-13089
Type: osv

## Details
OIDC::Lite versions through 0.12.1 for Perl allow ID Token signature verification bypass via a token-controlled algorithm allowlist in verify.

When the caller does not pin an algorithm, OIDC::Lite::Model::IDToken::verify sets $self->alg($self->header->{alg}) from the token's own header and then calls decode_jwt(token, key, 1, [$self->alg]), handing JSON::WebToken an accepted-algorithm allowlist taken from the untrusted token. A token with alg=none yields ['none'], so decode_jwt returns the claims with no signature check, and a token with alg=HS256 is verified with the RP's RSA public key as the HMAC secret (RS to HS confusion).

The ID Token is the OpenID Connect authentication assertion delivered to the Relying Party. Any caller that verifies an ID Token through the unpinned load(token)->verify path, or load(token, key) with only the key pinned, accepts a forged token carrying attacker-chosen claims such as sub and is authenticated as any user. Passing an explicit algorithm so $self->alg is already set bypasses the header-derived allowlist and is not affected.

Note that the latest version uploaded to CPAN is 0.10. Later versions are available in the git repository.

## References
- http://www.openwall.com/lists/oss-security/2026/07/22/17
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13089.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13089
- https://github.com/ritou/p5-oidc-lite/pull/31
- https://security.metacpan.org/patches/O/OIDC-Lite/0.10/CVE-2026-13089-r1.patch
- https://github.com/ritou/p5-oidc-lite
- https://datatracker.ietf.org/doc/html/rfc8725#section-3.1
