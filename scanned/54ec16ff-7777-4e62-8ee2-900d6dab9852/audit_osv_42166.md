# [M] CVE-2026-64777

## Summary
Severity: Medium
Advisory: CVE-2026-64777
Aliases: GHSA-2v2q-4q35-h585
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-64777
Type: osv

## Details
A malicious builder peer may be able to request an in-context file by name from the host and receive the contents of whatever the name resolves to, even when it resolves outside the build context. This vulnerability is addressed in container version 1.2.0.

## References
- https://github.com/apple/container/security/advisories/GHSA-2v2q-4q35-h585
