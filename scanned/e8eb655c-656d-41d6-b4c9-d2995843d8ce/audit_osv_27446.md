# [H] One-click remote code execution via malicious deep link

## Summary
Severity: High
Advisory: CVE-2024-21625
Aliases: GHSA-3v86-cf9q-x4x7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-04
Source: https://osv.dev/vulnerability/CVE-2024-21625
Type: osv

## Details
SideQuest is a place to get virtual reality applications for Oculus Quest. The SideQuest desktop application uses deep links with a custom protocol (`sidequest://`) to trigger actions in the application from its web contents. Because, prior to version 0.10.35, the deep link URLs were not sanitized properly in all cases, a one-click remote code execution can be achieved in cases when a device is connected, the user is presented with a malicious link and clicks it from within the application. As of version 0.10.35, the custom protocol links within the electron application are now being parsed and sanitized properly.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21625.json
- https://github.com/SideQuestVR/SideQuest/security/advisories/GHSA-3v86-cf9q-x4x7
- https://nvd.nist.gov/vuln/detail/CVE-2024-21625
