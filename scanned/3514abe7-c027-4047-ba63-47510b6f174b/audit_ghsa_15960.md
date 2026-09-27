# [M] ICG.AspNetCore.Utilities.CloudStorage's Secure Token Durations Different Than Expected

## Summary
Severity: Medium
Advisory: GHSA-24mc-gc52-47jv
CVE: CVE-2024-50353
CWE: CWE-284
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-30
Source: https://github.com/advisories/GHSA-24mc-gc52-47jv
Type: github-advisory

## Affected
- NuGet: `ICG.AspNetCore.Utilities.CloudStorage` — affected >=0 <8.0.0

## Details
### Impact
Users of this library that set a duration for a SAS Uri with a value other than 1 hour may have generated a URL with a duration that is longer, or shorter than desired.

Users not implemented SAS Uri's are unaffected.

### Patches
This issue was resolved in version 8.0.0 of the library, all users should update to this version ASAP.

### Workarounds
None

## References
- https://github.com/IowaComputerGurus/aspnetcore.utilities.cloudstorage/security/advisories/GHSA-24mc-gc52-47jv
- https://nvd.nist.gov/vuln/detail/CVE-2024-50353
- https://github.com/IowaComputerGurus/aspnetcore.utilities.cloudstorage/commit/8ea534481181a063175f457082662fdcad9a41ff
- https://github.com/IowaComputerGurus/aspnetcore.utilities.cloudstorage
