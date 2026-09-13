# [H] Crypt::SecretBuffer versions before 0.019 for Perl is suseceptible to timing attacks

## Summary
Severity: High
Advisory: CVE-2026-5086
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-5086
Type: osv

## Details
Crypt::SecretBuffer versions before 0.019 for Perl is suseceptible to timing attacks.

For example, if Crypt::SecretBuffer was used to store and compare plaintext passwords, then discrepencies in timing could be used to guess the secret password.

## References
- http://www.openwall.com/lists/oss-security/2026/04/13/12
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5086.json
- https://metacpan.org/release/NERDVANA/Crypt-SecretBuffer-0.019/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-5086
- https://github.com/nrdvana/perl-Crypt-SecretBuffer
