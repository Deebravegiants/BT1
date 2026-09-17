# [C] Lemonldap::NG::Portal versions from 2.0.0 before 2.16.9, from 2.17.0 before 2.21.5, from 2.22.0 before 2.23.3 for Perl allow authentication bypass via an OAuth2 state parameter stored as an SSO session in the GitHub and LinkedIn backends

## Summary
Severity: Critical
Advisory: CVE-2026-19349
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-16
Source: https://osv.dev/vulnerability/CVE-2026-19349
Type: osv

## Details
Lemonldap::NG::Portal versions from 2.0.0 before 2.16.9, from 2.17.0 before 2.21.5, from 2.22.0 before 2.23.3 for Perl allow authentication bypass via an OAuth2 state parameter stored as an SSO session in the GitHub and LinkedIn backends.

Before redirecting to the identity provider, extractFormInfo() creates the state session with the positional call `getApacheSession( undef, 1, 0, 'GitHubState' )`. getApacheSession() takes a session id followed by a named argument hash, so the trailing arguments become that hash, `kind` defaults to SSO, and the state is written to the global session storage as a regular SSO session. Its identifier is handed to the unauthenticated visitor as the state parameter of the redirection URL.

Any visitor who reaches the GitHub or LinkedIn endpoint can replay that identifier as a session cookie and obtain a valid SSO session without authenticating. The session holds neither _user nor authenticationLevel, which the shipped bootstrap configuration accepts because it grants virtual hosts a "default => accept" access rule; deployments whose rules test the user or require an authentication level are less exposed. Only configurations with the GitHub or LinkedIn authentication module enabled are affected.

## References
- http://www.openwall.com/lists/oss-security/2026/08/16/2
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19349.json
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/releases/v2.16.9
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/releases/v2.21.5
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/releases/v2.23.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-19349
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng
