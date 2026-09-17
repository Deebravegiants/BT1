# [M] CVE-2026-3099

## Summary
Severity: Medium
Advisory: CVE-2026-3099
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2026-3099
Type: osv

## Details
A flaw was found in Libsoup. The server-side digest authentication implementation in the SoupAuthDomainDigest class does not properly track issued nonces or enforce the required incrementing nonce-count (nc) attribute. This vulnerability allows a remote attacker to capture a single valid authentication header and replay it repeatedly. Consequently, the attacker can bypass authentication and gain unauthorized access to protected resources, impersonating the legitimate user.

## References
- https://access.redhat.com/security/cve/CVE-2026-3099
- https://bugzilla.redhat.com/show_bug.cgi?id=2442232
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/495
