# [C] Authen::SASL::Perl::DIGEST_MD5 versions before 2.2100 for Perl accept replayed authentication responses via unverified nonce in server_step

## Summary
Severity: Critical
Advisory: CVE-2026-86219
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/CVE-2026-86219
Type: osv

## Details
Authen::SASL::Perl::DIGEST_MD5 versions before 2.2100 for Perl accept replayed authentication responses via unverified nonce in server_step.

server_start generates a fresh nonce and sends it in the challenge, and nothing later compares that value against the nonce the client returns. server_step derives the expected digest from the client's own parameters, so a response verifies whenever its digest matches the nonce it carries. The count table it also checks is keyed on the client-supplied nonce and starts empty in each new server object, so a captured first response, carrying `nc=00000001`, passes that too. RFC 2831 defines the nonce in the response as the value the server sent in the preceding challenge.

An attacker who observes one successful `qop=auth` exchange can replay the captured response against a later session for the same service, host, realm and user, and authenticate as that user without knowing the password.

## References
- https://cpan.org/modules
- https://datatracker.ietf.org/doc/html/rfc2831#section-2.1.2
- https://metacpan.org/release/EHUELS/Authen-SASL-2.2000/source/lib/Authen/SASL/Perl/DIGEST_MD5.pm#L203-222
- https://metacpan.org/release/EHUELS/Authen-SASL-2.2000/source/lib/Authen/SASL/Perl/DIGEST_MD5.pm#L410-414
- https://www.cve.org/CVERecord?id=CVE-2025-40918
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86219.json
- https://metacpan.org/release/EHUELS/Authen-SASL-2.2100/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-86219
- https://github.com/perl-authen-sasl/perl-authen-sasl/commit/94337367030612842924f697cead29964a96448d.patch
- https://github.com/perl-authen-sasl/perl-authen-sasl
