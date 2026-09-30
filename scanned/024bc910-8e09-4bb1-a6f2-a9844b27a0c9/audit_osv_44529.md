# [M] LWP::UserAgent versions before 6.83 for Perl leak Authorization and Proxy-Authorization headers on cross-origin redirects

## Summary
Severity: Medium
Advisory: CVE-2026-8368
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-8368
Type: osv

## Details
LWP::UserAgent versions before 6.83 for Perl leak Authorization and Proxy-Authorization headers on cross-origin redirects.

On a 3xx response, the redirect handler strips only Host and Cookie before issuing the follow-up request. Caller-supplied Authorization and Proxy-Authorization headers are sent unchanged to the redirect target, including across scheme, host, or port changes.

A redirect to an attacker controlled host therefore discloses the caller's credentials to that host.

## References
- http://www.openwall.com/lists/oss-security/2026/05/12/7
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8368.json
- https://metacpan.org/release/OALDERS/libwww-perl-6.83/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8368
- https://github.com/libwww-perl/libwww-perl/pull/512
- https://github.com/libwww-perl/libwww-perl/commit/9c4aeb6f2dd32f2b7eaf2d7827cade31ea6cb2c6.patch
- https://github.com/libwww-perl/libwww-perl/pull/284
- https://github.com/libwww-perl/libwww-perl
