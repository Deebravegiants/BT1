# [M] CoreWCF: UnixDomainSocket Non-Reentrant POSIX Identity Resolution

## Summary
Severity: Medium
Advisory: GHSA-q6v9-43v5-jv9q
CVE: CVE-2026-54778
CWE: CWE-362, CWE-825
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-q6v9-43v5-jv9q
Type: github-advisory

## Affected
- NuGet: `CoreWCF.UnixDomainSocket` — affected >=0 <1.8.1
- NuGet: `CoreWCF.UnixDomainSocket` — affected >=1.9.0 <1.9.1

## Details
### Impact
Race condition in POSIX peer identity resolution may attribute one connection’s identity to another (getpwuid/getgrgid non-reentrant) and may crash the host process under contention.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
Restrict UDS filesystem permissions so that only trusted local users can connect to the socket path. The race still exists but the attacker pool is constrained.

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-q6v9-43v5-jv9q
- https://github.com/CoreWCF/CoreWCF
