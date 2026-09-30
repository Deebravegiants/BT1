# [M] ALPINE-CVE-2025-68160

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-68160
Ecosystem: Alpine:v3.17, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-68160
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.19-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.3.6-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.3.6-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.5-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.5-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.5-r0

## Details
Issue summary: Writing large, newline-free data into a BIO chain using the
line-buffering filter where the next BIO performs short writes can trigger
a heap-based out-of-bounds write.

Impact summary: This out-of-bounds write can cause memory corruption which
typically results in a crash, leading to Denial of Service for an application.

The line-buffering BIO filter (BIO_f_linebuffer) is not used by default in
TLS/SSL data paths. In OpenSSL command-line applications, it is typically
only pushed onto stdout/stderr on VMS systems. Third-party applications that
explicitly use this filter with a BIO chain that can short-write and that
write large, newline-free data influenced by an attacker would be affected.
However, the circumstances where this could happen are unlikely to be under
attacker control, and BIO_f_linebuffer is unlikely to be handling non-curated
data controlled by an attacker. For that reason the issue was assessed as
Low severity.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the BIO implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0, 1.1.1 and 1.0.2 are vulnerable to this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-68160
