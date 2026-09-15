# [H] CVE-2015-2319

## Summary
Severity: High
Advisory: CVE-2015-2319
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-08
Source: https://osv.dev/vulnerability/CVE-2015-2319
Type: osv

## Details
The TLS stack in Mono before 3.12.1 makes it easier for remote attackers to conduct cipher-downgrade attacks to EXPORT_RSA ciphers via crafted TLS traffic, related to the "FREAK" issue, a different vulnerability than CVE-2015-0204.

## References
- http://www.mono-project.com/news/2015/03/07/mono-tls-vulnerability/
- http://www.openwall.com/lists/oss-security/2015/03/17/9
- http://www.securityfocus.com/bid/73250
- http://www.ubuntu.com/usn/USN-2547-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1202869
- https://github.com/mono/mono/commit/9c38772f094168d8bfd5bc73bf8925cd04faad10
- https://mitls.org/pages/attacks/SMACK#freak
- https://www.debian.org/security/2015/dsa-3202
- http://www.openwall.com/lists/oss-security/2015/03/17/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1202869
