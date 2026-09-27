# [H] JLSEC-2026-778

## Summary
Severity: High
Advisory: JLSEC-2026-778
Ecosystem: Julia
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/JLSEC-2026-778
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.12.1+0

## Details
A flaw was found in libssh. This vulnerability allows local man-in-the-middle attacks, security downgrades of SSH (Secure Shell) connections, and manipulation of trusted host information, posing a significant risk to the confidentiality, integrity, and availability of SSH communications via an insecure default configuration on Windows systems where the library automatically loads configuration files from the `C:\etc` directory, which can be created and modified by unprivileged local users.

## References
- https://access.redhat.com/errata/RHSA-2026:7067
- https://access.redhat.com/security/cve/CVE-2025-14821
- https://bugzilla.redhat.com/show_bug.cgi?id=2423148
- https://www.libssh.org/2026/02/10/libssh-0-12-0-and-0-11-4-security-releases/
