# [C] Command Injection as root in NextCloudPi web panel

## Summary
Severity: Critical
Advisory: CVE-2024-30247
Aliases: GHSA-m597-72v7-j982
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-03-29
Source: https://osv.dev/vulnerability/CVE-2024-30247
Type: osv

## Details
NextcloudPi is a ready to use image for Virtual Machines, Raspberry Pi, Odroid HC1, Rock64 and other boards. A command injection vulnerability in NextCloudPi allows command execution as the root user via the NextCloudPi web-panel. Due to a security misconfiguration this can be used by anyone with access to NextCloudPi web-panel, no authentication is required. It is recommended that the NextCloudPi is upgraded to 1.53.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30247.json
- https://github.com/nextcloud/nextcloudpi/security/advisories/GHSA-m597-72v7-j982
- https://nvd.nist.gov/vuln/detail/CVE-2024-30247
