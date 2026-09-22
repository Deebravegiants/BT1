# [M] CVE-2021-47688

## Summary
Severity: Medium
Advisory: CVE-2021-47688
Aliases: GHSA-3f8r-9483-pfxj
CVSS: 5.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2021-47688
Type: osv

## Details
In WhiteBeam 0.2.0 through 0.2.1 before 0.2.2, a user with local access to a server can bypass the allow-list functionality because a file can be truncated in the OpenFileDescriptor action before the VerifyCanWrite action is performed.

## References
- https://github.com/WhiteBeamSec/WhiteBeam/security/policy
- https://github.com/WhiteBeamSec/WhiteBeam/security/advisories/GHSA-3f8r-9483-pfxj
- https://github.com/WhiteBeamSec/WhiteBeam/pull/22
