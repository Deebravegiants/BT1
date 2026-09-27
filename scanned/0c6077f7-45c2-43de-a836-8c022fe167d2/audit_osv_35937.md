# [C] Plack::App::Prerender versions before 0.3.0 for Perl can proxy to an arbitrary host via unvalidated REQUEST_URI concatenation in call

## Summary
Severity: Critical
Advisory: CVE-2026-17552
Aliases: GHSA-6x4w-x68j-ppqq
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-17552
Type: osv

## Details
Plack::App::Prerender versions before 0.3.0 for Perl can proxy to an arbitrary host via unvalidated REQUEST_URI concatenation in call.

When the rewrite base is a plain string, the REQUEST_URI is appended to it, with no check that the path starts with a forward slash ('/').

When the rewrite base does not contain a path (which is the standard given in the SYNOPSIS), an attacker can create a request that changes the hostname. A request target starting with an at-sign ('@') changes the base to a RFC 3986 userinfo component.

For example, a rewrite base of "https://example.com" with the submitted request "GET @192.168.1.2/" will send a request to "https://example.com@192.168.1.2/", with the rendered content returned to the attacker.

This allows an attacker to access internal or restricted hosts that only the webserver has access to.

## References
- http://www.openwall.com/lists/oss-security/2026/07/28/3
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17552.json
- https://github.com/robrwo/perl-Plack-App-Prerender/security/advisories/GHSA-6x4w-x68j-ppqq
- https://metacpan.org/release/RRWO/Plack-App-Prerender-v0.3.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-17552
- https://github.com/robrwo/perl-Plack-App-Prerender/commit/2d793dd69e2b6f4e469618ee742bd8402677202d.patch
- https://github.com/robrwo/perl-Plack-App-Prerender
