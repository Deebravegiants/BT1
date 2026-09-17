# [M] CVE-2021-32489

## Summary
Severity: Medium
Advisory: CVE-2021-32489
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-10
Source: https://osv.dev/vulnerability/CVE-2021-32489
Type: osv

## Details
An issue was discovered in the _send_secure_msg() function of Yubico yubihsm-shell through 2.0.3. The function does not correctly validate the embedded length field of an authenticated message received from the device because response_msg.st.len=8 can be accepted but triggers an integer overflow, which causes CRYPTO_cbc128_decrypt (in OpenSSL) to encounter an undersized buffer and experience a segmentation fault. The yubihsm-shell project is included in the YubiHSM 2 SDK product.

## References
- https://blog.inhq.net/posts/yubico-libyubihsm-vuln2/#second-attack-variant-cve-pending
