# [M] CVE-2021-21402

## Summary
Severity: Medium
Advisory: CVE-2021-21402
Aliases: GHSA-wg4c-c9g9-rxhx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/CVE-2021-21402
Type: osv

## Details
Jellyfin is a Free Software Media System. In Jellyfin before version 10.7.1, with certain endpoints, well crafted requests will allow arbitrary file read from a Jellyfin server's file system. This issue is more prevalent when Windows is used as the host OS. Servers that are exposed to the public Internet are potentially at risk. This is fixed in version 10.7.1. As a workaround, users may be able to restrict some access by enforcing strict security permissions on their filesystem, however, it is recommended to update as soon as possible.

## References
- https://github.com/jellyfin/jellyfin/releases/tag/v10.7.1
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-wg4c-c9g9-rxhx
- https://github.com/jellyfin/jellyfin/commit/0183ef8e89195f420c48d2600bc0b72f6d3a7fd7
