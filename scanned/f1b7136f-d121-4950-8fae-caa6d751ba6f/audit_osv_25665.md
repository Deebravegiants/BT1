# [H] OP-TEE double free in shdr_verify_signature

## Summary
Severity: High
Advisory: CVE-2023-41325
Aliases: GHSA-jrw7-63cq-7vhm
CVSS: 7.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/CVE-2023-41325
Type: osv

## Details
OP-TEE is a Trusted Execution Environment (TEE) designed as companion to a non-secure Linux kernel running on Arm; Cortex-A cores using the TrustZone technology. Starting in version 3.20 and prior to version 3.22, `shdr_verify_signature` can make a double free. `shdr_verify_signature` used to verify a TA binary before it is loaded. To verify a signature of it, allocate a memory for RSA key. RSA key allocate function (`sw_crypto_acipher_alloc_rsa_public_key`) will try to allocate a memory (which is optee’s heap memory). RSA key is consist of exponent and modulus (represent as variable `e`, `n`) and it allocation is not atomic way, so it may succeed in `e` but fail in `n`. In this case sw_crypto_acipher_alloc_rsa_public_key` will free on `e` and return as it is failed but variable ‘e’ is remained as already freed memory address . `shdr_verify_signature` will free again that memory (which is `e`) even it is freed when it failed allocate RSA key. A patch is available in version 3.22. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41325.json
- https://github.com/OP-TEE/optee_os/security/advisories/GHSA-jrw7-63cq-7vhm
- https://nvd.nist.gov/vuln/detail/CVE-2023-41325
- https://github.com/OP-TEE/optee_os/commit/e2ec831cb07ed0099535c7c140cb6338aa62816a
