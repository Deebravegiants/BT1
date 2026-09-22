# [M] A flaw was found in the key export functionality of libssh

## Summary
Severity: Medium
Advisory: JLSEC-2025-98
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-98
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.11.3+0

## Details
A flaw was found in the key export functionality of libssh. The issue occurs in the internal function responsible for converting cryptographic keys into serialized formats. During error handling, a memory structure is freed but not cleared, leading to a potential double free issue if an additional failure occurs later in the function. This condition may result in heap corruption or application instability in low-memory scenarios, posing a risk to system reliability where key export operations are performed.

## References
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/security/cve/CVE-2025-5351
- https://bugzilla.redhat.com/show_bug.cgi?id=2369367
