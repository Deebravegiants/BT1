# [C] CVE-2024-2362

## Summary
Severity: Critical
Advisory: CVE-2024-2362
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-2362
Type: osv

## Details
A path traversal vulnerability exists in the parisneo/lollms-webui version 9.3 on the Windows platform. Due to improper validation of file paths between Windows and Linux environments, an attacker can exploit this vulnerability to delete any file on the system. The issue arises from the lack of adequate sanitization of user-supplied input in the 'del_preset' endpoint, where the application fails to prevent the use of absolute paths or directory traversal sequences ('..'). As a result, an attacker can send a specially crafted request to the 'del_preset' endpoint to delete files outside of the intended directory.

## References
- https://huntr.com/bounties/2433d0a4-9ba0-474b-be1a-6fd5019770ba
