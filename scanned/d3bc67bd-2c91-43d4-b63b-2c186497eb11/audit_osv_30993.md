# [C] CVE-2024-5752

## Summary
Severity: Critical
Advisory: CVE-2024-5752
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-5752
Type: osv

## Details
A path traversal vulnerability exists in stitionai/devika, specifically in the project creation functionality. In the affected version beacf6edaa205a5a5370525407a6db45137873b3, the project name is not validated, allowing an attacker to create a project with a crafted name that traverses directories. This can lead to arbitrary file overwrite when the application generates code and saves it to the specified project directory, potentially resulting in remote code execution.

## References
- https://huntr.com/bounties/865b5f44-ef75-4243-a5f1-2f0d895353b1
- https://github.com/stitionai/devika/commit/6acce21fb08c3d1123ef05df6a33912bf0ee77c2
