# [H] CVE-2018-1000649

## Summary
Severity: High
Advisory: CVE-2018-1000649
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000649
Type: osv

## Details
LibreHealthIO lh-ehr version REL-2.0.0 contains a Authenticated Unrestricted File Write in letter.php (2) vulnerability in Patient file letter functions that can result in Write files with malicious content and may lead to remote code execution. This attack appear to be exploitable via User controlled input.

## References
- https://0dd.zone/2018/08/07/lh-ehr-Authenticated-File-Write-Letter-PHP-2/
- https://github.com/LibreHealthIO/lh-ehr/issues/1214
