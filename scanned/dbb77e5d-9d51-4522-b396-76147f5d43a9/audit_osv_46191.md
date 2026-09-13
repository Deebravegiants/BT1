# [M] JLSEC-2026-782

## Summary
Severity: Medium
Advisory: JLSEC-2026-782
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/JLSEC-2026-782
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.11.4+0

## Details
A flaw was found in libssh. A remote attacker, by controlling client configuration files or `known_hosts` files, could craft specific hostnames that when processed by the `match_pattern()` function can lead to inefficient regular expression backtracking. This can cause timeouts and resource exhaustion, resulting in a Denial of Service (DoS) for the client.

## References
- https://access.redhat.com/errata/RHSA-2026:18160
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/security/cve/CVE-2026-0967
- https://bugzilla.redhat.com/show_bug.cgi?id=2436981
- https://www.libssh.org/2026/02/10/libssh-0-12-0-and-0-11-4-security-releases/
