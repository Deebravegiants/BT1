# [C] Net::OAuth::Client versions before 0.32 for Perl allow the service provider to silently downgrade OAuth 1.0a to OAuth 1.0 in get_request_token

## Summary
Severity: Critical
Advisory: CVE-2026-72887
Aliases: GHSA-jh72-4qq2-8j6g
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-16
Source: https://osv.dev/vulnerability/CVE-2026-72887
Type: osv

## Details
Net::OAuth::Client versions before 0.32 for Perl allow the service provider to silently downgrade OAuth 1.0a to OAuth 1.0 in get_request_token.

Passing a callback to the constructor selects OAuth 1.0a. get_request_token then revokes that choice when the request token response omits oauth_callback_confirmed, with no exception, no warning and no option to require 1.0a. The access token request is built from the OAuth 1.0 message class, which has no verifier parameter, so oauth_verifier is dropped from the request even when get_access_token was passed one.

oauth_verifier is the binding that OAuth 1.0a added between the authorization step and the token exchange. An application that asked for 1.0a and gets 1.0 is open to OAuth 1.0 session fixation, where an attacker obtains a request token, has the victim authorize it, and then completes the exchange themselves, linking the victim's provider account to a session the attacker controls. No attacker action sets up the downgrade: a provider that does not confirm the callback is enough.

## References
- http://www.openwall.com/lists/oss-security/2026/08/16/3
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72887.json
- https://github.com/vurtdev/Net-OAuth/security/advisories/GHSA-jh72-4qq2-8j6g
- https://metacpan.org/release/RRWO/Net-OAuth-0.32/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-72887
- https://github.com/vurtdev/Net-OAuth/commit/fd505dac1988723ed96721657663f2e4ac731644.patch
- https://github.com/vurtdev/Net-OAuth
- https://datatracker.ietf.org/doc/html/rfc5849#section-2.1
- https://datatracker.ietf.org/doc/html/rfc5849#section-2.3
