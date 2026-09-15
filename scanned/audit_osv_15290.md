# [M] CVE-2019-15032

## Summary
Severity: Medium
Advisory: CVE-2019-15032
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-15032
Type: osv

## Details
Pydio 6.0.8 mishandles error reporting when a directory allows unauthenticated uploads, and the remote-upload option is used with the http://localhost:22 URL. The attacker can obtain sensitive information such as the name of the user who created that directory and other internal server information.

## References
- https://pydio.com
- https://sourceforge.net/projects/ajaxplorer/files/pydio/stable-channel/
- https://heitorgouvea.me/2019/09/17/CVE-2019-15032
