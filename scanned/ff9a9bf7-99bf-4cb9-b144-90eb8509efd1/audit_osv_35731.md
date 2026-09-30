# [H] Dancer::Plugin::Auth::Google versions before 0.08 for Perl have TLS verification disabled

## Summary
Severity: High
Advisory: CVE-2026-13410
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-13410
Type: osv

## Details
Dancer::Plugin::Auth::Google versions before 0.08 for Perl have TLS verification disabled.

The default user agent is initialised with SSL_verify_mode explicitly disabled.

An attacker with network man-in-the-middle (MITM) capability between the Dancer application and googleapis.com can intercept the OAuth2 token exchange and userinfo fetch, return a forged access_token and user profile, and be logged in to the Dancer application as any Google user.

## References
- http://www.openwall.com/lists/oss-security/2026/07/17/8
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13410.json
- https://metacpan.org/release/GARU/Dancer-Plugin-Auth-Google-0.08/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-13410
- https://github.com/garu/Dancer-Plugin-Auth-Google/pull/5
- https://github.com/garu/Dancer-Plugin-Auth-Google/commit/2fdb72527eaa0e11a5c134c597f1e44e37411d95.patch
- https://security.metacpan.org/patches/D/Dancer-Plugin-Auth-Google/0.07/CVE-2026-13410-r1.patch
- https://github.com/garu/Dancer-Plugin-Auth-Google
- https://metacpan.org/pod/Furl#HTTPS-requests-claims-warnings!
