# [C] CVE-2024-1305

## Summary
Severity: Critical
Advisory: CVE-2024-1305
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/CVE-2024-1305
Type: osv

## Details
tap-windows6 driver version 9.26 and earlier does not properly 
check the size data of incomming write operations which an attacker can 
use to overflow memory buffers, resulting in a bug check and potentially
 arbitrary code execution in kernel space

## References
- https://community.openvpn.net/openvpn/wiki/CVE-2024-1305
- https://www.mail-archive.com/openvpn-users@lists.sourceforge.net/msg07534.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1305.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1305
