# [C] NuGet Gallery: Arbitrary Blob Overwrite via Nuspec Confusion and URI Fragment Truncation

## Summary
Severity: Critical
Advisory: CVE-2026-39399
Aliases: GHSA-9r3h-v4hx-rhfr
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-39399
Type: osv

## Details
NuGet Gallery is a package repository that powers nuget.org. A security vulnerability exists in the NuGetGallery backend job’s handling of .nuspec files within NuGet packages. An attacker can supply a crafted nuspec file with malicious metadata, leading to cross package metadata injection that may result in remote code execution (RCE) and/or arbitrary blob writes due to insufficient input validation. The issue is exploitable via URI fragment injection using unsanitized package identifiers, allowing an attacker to control the resolved blob path. This enables writes to arbitrary blobs within the storage container, not limited to .nupkg files, resulting in potential tampering of existing content. This issue has been patched in commit 0e80f87628349207cdcaf55358491f8a6f1ca276.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39399.json
- https://github.com/NuGet/NuGetGallery/security/advisories/GHSA-9r3h-v4hx-rhfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-39399
- https://github.com/NuGet/NuGetGallery/commit/0e80f87628349207cdcaf55358491f8a6f1ca276
