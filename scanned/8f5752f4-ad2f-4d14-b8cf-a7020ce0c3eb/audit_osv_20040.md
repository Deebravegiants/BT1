# [M] CVE-2021-29490

## Summary
Severity: Medium
Advisory: CVE-2021-29490
Aliases: GHSA-rgjw-4fwc-9v96
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-29490
Type: osv

## Details
Jellyfin is a free software media system that provides media from a dedicated server to end-user devices via multiple apps. Verions prior to 10.7.3 vulnerable to unauthenticated Server-Side Request Forgery (SSRF) attacks via the imageUrl parameter. This issue potentially exposes both internal and external HTTP servers or other resources available via HTTP `GET` that are visible from the Jellyfin server. The vulnerability is patched in version 10.7.3. As a workaround, disable external access to the API endpoints `/Items/*/RemoteImages/Download`, `/Items/RemoteSearch/Image` and `/Images/Remote` via reverse proxy, or limit to known-friendly IPs.

## References
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-rgjw-4fwc-9v96
