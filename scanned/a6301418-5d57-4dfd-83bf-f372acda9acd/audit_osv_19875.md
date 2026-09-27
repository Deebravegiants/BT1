# [M] CVE-2021-27217

## Summary
Severity: Medium
Advisory: CVE-2021-27217
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/CVE-2021-27217
Type: osv

## Details
An issue was discovered in the _send_secure_msg() function of Yubico yubihsm-shell through 2.0.3. The function does not correctly validate the embedded length field of an authenticated message received from the device. Out-of-bounds reads performed by aes_remove_padding() can crash the running process, depending on the memory layout. This could be used by an attacker to cause a client-side denial of service. The yubihsm-shell project is included in the YubiHSM 2 SDK product.

## References
- https://github.com/Yubico/yubihsm-shell/releases
- https://www.yubico.com/support/security-advisories/ysa-2021-01/
- https://blog.inhq.net/posts/yubico-libyubihsm-vuln2
