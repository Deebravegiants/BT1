# [C] CVE-2025-29266

## Summary
Severity: Critical
Advisory: CVE-2025-29266
CVSS: 9.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-03-31
Source: https://osv.dev/vulnerability/CVE-2025-29266
Type: osv

## Details
Unraid 7.0.0 before 7.0.1 allows remote users to access the Unraid WebGUI and web console as root without authentication if a container is running in Host networking mode with Use Tailscale enabled.

## References
- https://docs.unraid.net/unraid-os/release-notes/7.0.1/
- https://edac.dev/security/CVE-2025-29266/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29266.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29266
- https://github.com/unraid/webgui
