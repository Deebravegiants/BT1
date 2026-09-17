# [C] OP-TEE OS 4.10.0 Buffer Underwrite via RSA NOPAD Encrypt/Decrypt Operations

## Summary
Severity: Critical
Advisory: CVE-2026-71969
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-71969
Type: osv

## Details
OP-TEE OS through 4.10.0, fixed in commit 7b8b494, contains a buffer underwrite vulnerability in the RSA NOPAD encrypt and decrypt operations within the mbedTLS software backend and SE050 hardware driver that allows a malicious Trusted Application to corrupt secure-world heap memory by supplying an input length exceeding the RSA modulus size. When src_len exceeds rsa_len, the subtraction expression wraps to a large unsigned value, causing a subsequent memcpy to write attacker-controlled data before the destination buffer in S-EL1 secure-world heap memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71969.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71969
- https://www.vulncheck.com/advisories/op-tee-os-buffer-underwrite-via-rsa-nopad-encrypt-decrypt-operations
- https://github.com/OP-TEE/optee_os/pull/7808
- https://github.com/OP-TEE/optee_os/pull/7898
- https://github.com/OP-TEE/optee_os/commit/7b8b494e0a324cefec8ed386b7de413b44f1aaf3
- https://github.com/OP-TEE/optee_os
- https://blog.secmate.dev/posts/optee-vulnerabilities-disclosure/
