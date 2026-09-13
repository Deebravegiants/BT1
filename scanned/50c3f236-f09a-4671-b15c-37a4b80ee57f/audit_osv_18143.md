# [H] CVE-2020-24388

## Summary
Severity: High
Advisory: CVE-2020-24388
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-19
Source: https://osv.dev/vulnerability/CVE-2020-24388
Type: osv

## Details
An issue was discovered in the _send_secure_msg() function of yubihsm-shell through 2.0.2. The function does not validate the embedded length field of a message received from the device. This could lead to an oversized memcpy() call that will crash the running process. This could be used by an attacker to cause a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y77KQJW76M3PFOBFLBT6DLH2NWHYRNZO/
- https://developers.yubico.com/yubihsm-shell/
- https://github.com/Yubico/yubihsm-shell
- https://www.yubico.com/support/security-advisories/ysa-2020-06/
- https://blog.inhq.net/posts/yubico-libyubihsm-vuln/
