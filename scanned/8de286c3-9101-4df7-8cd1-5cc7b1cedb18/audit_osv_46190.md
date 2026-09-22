# [H] JLSEC-2026-781

## Summary
Severity: High
Advisory: JLSEC-2026-781
Ecosystem: Julia
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/JLSEC-2026-781
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.11.4+0

## Details
A flaw was found in libssh. The API function `ssh_get_hexa()` is vulnerable to a denial of service when processing zero-length input. This can be exploited remotely by an attacker during GSSAPI (Generic Security Service Application Program Interface) authentication if the server's logging verbosity is set to `SSH_LOG_PACKET (3)` or higher. Successful exploitation could lead to a self-Denial of Service of the per-connection daemon process.

## References
- https://access.redhat.com/errata/RHSA-2026:18160
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/errata/RHSA-2026:7067
- https://access.redhat.com/security/cve/CVE-2026-0966
- https://bugzilla.redhat.com/show_bug.cgi?id=2433121
- https://www.libssh.org/2026/02/10/libssh-0-12-0-and-0-11-4-security-releases/
