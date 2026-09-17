# [H] EVerest's inadequate session handling can lead to memory-related errors or exhaustion of the operating system’s file descriptors, resulting in a denial of service

## Summary
Severity: High
Advisory: CVE-2025-68136
Aliases: GHSA-4h8h-x5cp-g22r
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-68136
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2025.10.0, once the module receives a SDP request, it creates a whole new set of objects like `Session`, `IConnection` which open new TCP socket for the ISO15118-20 communications and registers callbacks for the created file descriptor, without closing and destroying the previous ones. Previous `Session` is not saved and the usage of an `unique_ptr` is lost, destroying connection data. Latter, if the used socket and therefore file descriptor is not the last one, it will lead to a null pointer dereference. Version 2025.10.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68136.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-4h8h-x5cp-g22r
- https://nvd.nist.gov/vuln/detail/CVE-2025-68136
