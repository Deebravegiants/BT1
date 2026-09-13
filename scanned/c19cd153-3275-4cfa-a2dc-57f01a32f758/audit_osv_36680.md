# [M] Budibase Vulnerable to Privilege Escalation via API Abuse – Creator Can Invite Users with Admin/Any Role

## Summary
Severity: Medium
Advisory: CVE-2026-25040
Aliases: GHSA-4wfw-r86x-qxrm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-25040
Type: osv

## Details
Budibase is a low code platform for creating internal tools, workflows, and admin panels. In versions up to and including 3.26.3, a Creator-level user, who normally has no UI permission to invite users, can manipulate API requests to invite new users with any role, including Admin, Creator, or App Viewer, and assign them to any group in the organization. This allows full privilege escalation, bypassing UI restrictions, and can lead to complete takeover of the workspace or organization. As of time of publication, no known fixed versions are available.

## References
- https://drive.google.com/file/d/1Dtn1WLJILRYUeoMjEbUfCbqQ3g2AW2Qz/view?usp=sharing
- https://github.com/user-attachments/files/22066135/budibase-privileged-esc-poc.txt
- https://github.com/Budibase/budibase/security/advisories/GHSA-4wfw-r86x-qxrm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25040.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25040
