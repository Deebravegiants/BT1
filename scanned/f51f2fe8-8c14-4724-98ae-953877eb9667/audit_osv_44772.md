# [M] Webstudio through 0.296.0 SSRF via /cgi proxy routes

## Summary
Severity: Medium
Advisory: CVE-2026-86119
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86119
Type: osv

## Details
Webstudio through 0.296.0 contains an unauthenticated server-side request forgery vulnerability in the /cgi/image, /cgi/video, and /cgi/asset proxy routes when RESIZE_ORIGIN environment variable is unset. Attackers can supply arbitrary URLs to these endpoints to read cloud instance metadata, access internal services, and perform network reconnaissance on the instance infrastructure.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86119.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86119
- https://www.vulncheck.com/advisories/webstudio-through-0.296.0-ssrf-via-cgi-proxy-routes
- https://github.com/webstudio-is/webstudio/issues/5816
- https://github.com/webstudio-is/webstudio
- https://github.com/webstudio-is/webstudio/blob/55920c57c4d3e128a0fa48fceabbbc3a1d73f1ef/apps/builder/app/routes/cgi.asset.$.ts
- https://github.com/webstudio-is/webstudio/blob/55920c57c4d3e128a0fa48fceabbbc3a1d73f1ef/apps/builder/app/routes/cgi.image.$.ts
- https://github.com/webstudio-is/webstudio/blob/55920c57c4d3e128a0fa48fceabbbc3a1d73f1ef/apps/builder/app/routes/cgi.video.$.ts
