# [C] CVE-2023-51803

## Summary
Severity: Critical
Advisory: CVE-2023-51803
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-31
Source: https://osv.dev/vulnerability/CVE-2023-51803
Type: osv

## Details
LinuxServer.io Heimdall before 2.5.7 does not prevent use of icons that have non-image data such as the "<?php ?>" substring.

## References
- https://github.com/linuxserver/Heimdall/releases/tag/v2.5.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51803.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-51803
- https://github.com/linuxserver/Heimdall/pull/1167
- https://github.com/linuxserver/Heimdall/pull/1173
