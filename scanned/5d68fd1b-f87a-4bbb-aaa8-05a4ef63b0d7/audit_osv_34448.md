# [M] Termix' official Docker image contains an authentication bypass vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-59951
Aliases: GHSA-92cw-877q-6r94
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-59951
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. The official Docker image  for Termix versions 1.5.0 and below, due to being configured with an Nginx reverse proxy, causes the backend to retrieve the proxy's IP instead of the client's IP when using the req.ip method. This results in isLocalhost always returning True. Consequently, the /ssh/db/host/internal endpoint can be accessed directly without login or authentication. This endpoint records the system's stored SSH host information, including addresses, usernames, and passwords, posing an extremely high security risk. Users who use the official Termix docker image, build their own image using the official dockerfile, or utilize reverse proxy functionality will be affected by this vulnerability. This issue is fixed in version 1.6.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59951.json
- https://github.com/LukeGus/Termix/security/advisories/GHSA-92cw-877q-6r94
- https://nvd.nist.gov/vuln/detail/CVE-2025-59951
- https://github.com/LukeGus/Termix/pull/221
