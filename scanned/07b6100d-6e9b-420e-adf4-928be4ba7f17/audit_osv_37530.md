# [M] Tautulli: Unauthenticated pms_image_proxy endpoint proxies arbitrary HTTP requests through the Plex Media Server

## Summary
Severity: Medium
Advisory: CVE-2026-31804
Aliases: GHSA-qj2f-4c4p-wv97
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-31804
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. Prior to version 2.17.0, the /pms_image_proxy endpoint accepts a user-supplied img parameter and forwards it to Plex Media Server's /photo/:/ transcode transcoder without authentication and without restricting the scheme or host. The endpoint is intentionally excluded from all authentication checks in webstart.py, any value of img beginning with http is passed directly to Plex, this causes the Plex Media Server process, which typically runs on the same host or internal network as Tautulli, with access to RFC-1918 address space, to issue an outbound HTTP request to any attacker-specified URL. This issue has been patched in version 2.17.0.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31804.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-qj2f-4c4p-wv97
- https://nvd.nist.gov/vuln/detail/CVE-2026-31804
