# [M] CVE-2018-25100

## Summary
Severity: Medium
Advisory: CVE-2018-25100
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-03-24
Source: https://osv.dev/vulnerability/CVE-2018-25100
Type: osv

## Details
The Mojolicious module before 7.66 for Perl may leak cookies in certain situations related to multiple similar cookies for the same domain. This affects Mojo::UserAgent::CookieJar.

## References
- https://metacpan.org/dist/Mojolicious/changes
- https://github.com/mojolicious/mojo/issues/1185
- https://github.com/mojolicious/mojo/commit/c16a56a9d6575ddc53d15e76d58f0ebcb0eeb149
- https://github.com/mojolicious/mojo/pull/1192
