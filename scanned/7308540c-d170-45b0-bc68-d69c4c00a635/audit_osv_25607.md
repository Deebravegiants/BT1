# [C] Automate Vulnerable to Malicious Content Uploaded Through Embedded Compliance Application

## Summary
Severity: Critical
Advisory: CVE-2023-40050
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-10-31
Source: https://osv.dev/vulnerability/CVE-2023-40050
Type: osv

## Details
Upload profile either
through API or user interface in Chef Automate prior to and including version 4.10.29 using InSpec
check command with maliciously crafted profile allows remote code execution.

## References
- https://www.chef.io/downloads
- https://community.progress.com/s/article/Product-Alert-Bulletin-October-2023-CHEF-Automate-CVE-2023-40050
- https://docs.chef.io/automate/profiles/
- https://docs.chef.io/release_notes_automate/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40050.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40050
- https://github.com/chef/automate
