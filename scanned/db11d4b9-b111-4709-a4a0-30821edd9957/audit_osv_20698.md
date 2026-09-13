# [H] CVE-2021-36218

## Summary
Severity: High
Advisory: CVE-2021-36218
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-27
Source: https://osv.dev/vulnerability/CVE-2021-36218
Type: osv

## Details
An issue was discovered in SKALE sgxwallet 1.58.3. sgx_disp_ippsAES_GCMEncrypt allows an out-of-bounds write, resulting in a segfault and compromised enclave. This issue describes a buffer overflow, which was resolved prior to v1.77.0 and not reproducible in latest sgxwallet v1.77.0

## References
- https://github.com/skalenetwork/sgxwallet/releases
- https://github.com/skalenetwork/sgxwallet/commit/77425c862ad20cd270d42c54f3d63e1eb4e02195
