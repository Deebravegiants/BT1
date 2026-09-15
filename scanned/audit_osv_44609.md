# [M] Apache::Session::Generate::SHA256 versions before 1.3.19 for Perl create insecure session ids

## Summary
Severity: Medium
Advisory: CVE-2026-8503
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-8503
Type: osv

## Details
Apache::Session::Generate::SHA256 versions before 1.3.19 for Perl create insecure session ids.

Apache::Session::Generate::SHA256 generated session ids insecurely. The default session id generator returns a SHA-256 hash of the built-in rand() function, the epoch time, and the PID, that is hashed again. These are predictable, low-entropy sources. Predicable session ids could allow an attacker to gain access to systems.

Note that version 1.3.19 has a fallback without warning to use insecure session generation method if the call to Crypt::URandom::urandom fails. However, this is unlikely as Crypt::URandom is a hardcoded requirement of the module.

This issue is similar to CVE-2025-40931 for Apache::Session::Generate::MD5.

## References
- https://cpan.org/modules
- https://metacpan.org/release/GUIMARD/Apache-Session-Browseable-1.3.19/diff/GUIMARD/Apache-Session-Browseable-1.3.18#lib/Apache/Session/Generate/SHA256.pm
- https://www.cve.org/CVERecord?id=CVE-2025-40931
- https://www.cve.org/CVERecord?id=CVE-2025-40932
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8503.json
- https://metacpan.org/release/GUIMARD/Apache-Session-Browseable-1.3.19/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8503
- https://github.com/LemonLDAPNG/Apache-Session-Browseable/commit/cc915cbbd266776eec3dd8bf4748b15fa827dbd0.patch
- https://github.com/LemonLDAPNG/Apache-Session-Browseable
