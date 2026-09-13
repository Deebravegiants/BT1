# [M] CVE-2018-9839

## Summary
Severity: Medium
Advisory: CVE-2018-9839
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-06
Source: https://osv.dev/vulnerability/CVE-2018-9839
Type: osv

## Details
An issue was discovered in MantisBT through 1.3.14, and 2.0.0. Using a crafted request on bug_report_page.php (modifying the 'm_id' parameter), any user with REPORTER access or above is able to view any private issue's details (summary, description, steps to reproduce, additional information) when cloning it. By checking the 'Copy issue notes' and 'Copy attachments' checkboxes and completing the clone operation, this data also becomes public (except private notes).

## References
- https://mantisbt.org/bugs/view.php?id=24221
- https://github.com/mantisbt/mantisbt/commit/1fbcd9bca2f2c77cb61624d36ddee4b3802c38ea
