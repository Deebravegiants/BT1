# [H] Mojolicious versions from 0.999922 for Perl uses a hard coded string, or the application's class name, as an HMAC session cookie secret by default

## Summary
Severity: High
Advisory: CVE-2024-58134
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-05-03
Source: https://osv.dev/vulnerability/CVE-2024-58134
Type: osv

## Details
Mojolicious versions from 0.999922 for Perl uses a hard coded string, or the application's class name, as an HMAC session cookie secret by default.

These predictable default secrets can be exploited by an attacker to forge session cookies.  An attacker who knows or guesses the secret could compute valid HMAC signatures for the session cookie, allowing them to tamper with or hijack another user’s session.

## References
- https://cpan.org/modules
- https://metacpan.org/release/SRI/Mojolicious-9.39/source/lib/Mojolicious.pm#L51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58134.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58134
- https://github.com/mojolicious/mojo/pull/1791
- https://github.com/mojolicious/mojo/pull/2200
- https://github.com/mojolicious/mojo/pull/2252
- https://github.com/mojolicious/mojo
- https://docs.mojolicious.org/Mojolicious/Guides/FAQ#What-does-Your-secret-passphrase-needs-to-be-changed-mean
- https://lists.debian.org/debian-perl/2025/05/msg00016.html
- https://lists.debian.org/debian-perl/2025/05/msg00017.html
- https://lists.debian.org/debian-perl/2025/05/msg00018.html
- https://medium.com/securing/baking-mojolicious-cookies-revisited-a-case-study-of-solving-security-problems-through-security-by-13da7c225802
- https://www.synacktiv.com/publications/baking-mojolicious-cookies
- https://github.com/hashcat/hashcat/pull/4090
