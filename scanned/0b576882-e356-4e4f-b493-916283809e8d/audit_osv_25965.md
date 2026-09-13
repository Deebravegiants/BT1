# [H] Jellyfin Possible Remote Code Execution via custom FFmpeg binary

## Summary
Severity: High
Advisory: CVE-2023-48702
Aliases: GHSA-rr9h-w522-cvmr
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-48702
Type: osv

## Details
Jellyfin is a system for managing and streaming media. Prior to version 10.8.13, the `/System/MediaEncoder/Path` endpoint executes an arbitrary file using `ProcessStartInfo` via the `ValidateVersion` function. A malicious administrator can setup a network share and supply a UNC path to `/System/MediaEncoder/Path` which points to an executable on the network share, causing Jellyfin server to run the executable in the local context. The endpoint was removed in version 10.8.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48702.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-rr9h-w522-cvmr
- https://nvd.nist.gov/vuln/detail/CVE-2023-48702
- https://securitylab.github.com/advisories/GHSL-2023-028_jellyfin/
- https://github.com/jellyfin/jellyfin/commit/83d2c69516471e2db72d9273c6a04247d0f37c86
