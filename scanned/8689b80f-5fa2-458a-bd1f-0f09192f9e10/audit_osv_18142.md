# [H] CVE-2020-24387

## Summary
Severity: High
Advisory: CVE-2020-24387
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-19
Source: https://osv.dev/vulnerability/CVE-2020-24387
Type: osv

## Details
An issue was discovered in the yh_create_session() function of yubihsm-shell through 2.0.2. The function does not explicitly check the returned session id from the device. An invalid session id would lead to out-of-bounds read and write operations in the session array. This could be used by an attacker to cause a denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y77KQJW76M3PFOBFLBT6DLH2NWHYRNZO/
- https://developers.yubico.com/yubihsm-shell/
- https://github.com/Yubico/yubihsm-shell
- https://www.yubico.com/support/security-advisories/ysa-2020-06/
- https://blog.inhq.net/posts/yubico-libyubihsm-vuln/
