# [M] Mojolicious versions from 7.28 through 9.45 for Perl will generate weak HMAC session cookie secrets via "mojo generate app" by default

## Summary
Severity: Medium
Advisory: CVE-2024-58135
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-05-03
Source: https://osv.dev/vulnerability/CVE-2024-58135
Type: osv

## Details
Mojolicious versions from 7.28 through 9.45 for Perl will generate weak HMAC session cookie secrets via "mojo generate app" by default.

When creating a default app skeleton with the "mojo generate app" tool, a weak secret is written to the application's configuration file using the insecure rand() function, and used for authenticating and protecting the integrity of the application's sessions. This may allow an attacker to brute force the application's session keys.

Release 9.46 fixes the issue by providing high quality randomness, even in absence of CryptX.

Users should be aware that the update does not replace previously generated weak secrets.  A secret generated with the previous version MUST be replaced to ensure the updated version is using a strong secret.

## References
- https://cpan.org/modules
- https://metacpan.org/release/SRI/Mojolicious-7.28/source/lib/Mojolicious/Command/generate/app.pm#L220
- https://metacpan.org/release/SRI/Mojolicious-9.38/source/lib/Mojolicious/Command/Author/generate/app.pm#L202
- https://metacpan.org/release/SRI/Mojolicious-9.39/source/lib/Mojo/Util.pm#L181
- https://perldoc.perl.org/functions/rand
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58135.json
- https://metacpan.org/release/SRI/Mojolicious-9.46/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2024-58135
- https://github.com/mojolicious/mojo/pull/2200
- https://github.com/mojolicious/mojo/commit/789cfa43f9118852b38cbd1fd0a2596bcb9821ea.patch
- https://github.com/mojolicious/mojo/commit/fb3733f92cc8a3344e6d615b3c7dac9d538eeab0.patch
- https://github.com/mojolicious/mojo
- https://lists.debian.org/debian-perl/2025/05/msg00016.html
- https://lists.debian.org/debian-perl/2025/05/msg00017.html
- https://lists.debian.org/debian-perl/2025/05/msg00018.html
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://github.com/hashcat/hashcat/pull/4090
