# [H] CVE-2018-1000648

## Summary
Severity: High
Advisory: CVE-2018-1000648
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000648
Type: osv

## Details
LibreHealthIO lh-ehr version REL-2.0.0 contains a Authenticated Unrestricted File Write vulnerability in Patient file letter functions that can result in Write files with malicious content and may lead to remote code execution. This attack appear to be exploitable via User controlled parameters.

## References
- https://0dd.zone/2018/08/07/lh-ehr-Authenticated-File-Write-Letter-PHP/
- https://github.com/LibreHealthIO/lh-ehr/issues/1213
