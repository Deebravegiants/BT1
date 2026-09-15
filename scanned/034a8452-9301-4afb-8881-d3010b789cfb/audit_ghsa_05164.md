# [M] CoreWCF NetNamedPipe transport accepts attach to a pre-existing named pipe instance

## Summary
Severity: Medium
Advisory: GHSA-6jj2-4q5c-x8g6
CVE: CVE-2026-54777
CWE: CWE-367, CWE-665
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6jj2-4q5c-x8g6
Type: github-advisory

## Affected
- NuGet: `CoreWCF.NetNamedPipe` — affected >=0 <1.8.1
- NuGet: `CoreWCF.NetNamedPipe` — affected >=1.9.0 <1.9.1

## Details
### Impact
CoreWCF NetNamedPipe transport accepts attach to a pre-existing named pipe instance, allowing local interception of NetNamedPipe traffic. NetNamedPipe creates a shared memory object based on the listening url, then generated a unique GUID for the named pipe it will be using and saves this to the shared memory object. Then it creates the named pipe to listen for clients. This requires an attacker to race the service and create the named pipe between the service publishing the GUID to the shared memory location (which the attacker needs to read) and the service creating the named pipe itself.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
None

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-6jj2-4q5c-x8g6
- https://github.com/CoreWCF/CoreWCF
