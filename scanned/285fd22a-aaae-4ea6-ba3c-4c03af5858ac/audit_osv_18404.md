# [H] CVE-2020-27385

## Summary
Severity: High
Advisory: CVE-2020-27385
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-11-12
Source: https://osv.dev/vulnerability/CVE-2020-27385
Type: osv

## Details
Incorrect Access Control in the FileEditor (/Admin/Views/FileEditor/) in FlexDotnetCMS before v1.5.11 allows an authenticated remote attacker to read and write to existing files outside the web root. The files can be accessed via directory traversal, i.e., by entering a .. (dot dot) path such as ..\..\..\..\..\<file> in the input field of the FileEditor. In FlexDotnetCMS before v1.5.8, it is also possible to access files by specifying the full path (e.g., C:\<file>). The files can then be edited via the FileEditor.

## References
- https://github.com/MacdonaldRobinson/FlexDotnetCMS/releases/tag/v1.5.11
- https://blog.vonahi.io/whats-in-a-re-name/
