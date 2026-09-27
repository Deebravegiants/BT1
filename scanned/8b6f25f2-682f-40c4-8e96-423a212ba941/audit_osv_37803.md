# [H] OP-TEE: PKCS#11 TA out-of-bounds read and memory disclosure

## Summary
Severity: High
Advisory: CVE-2026-33317
Aliases: GHSA-8cqw-mg7v-c9p9
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-33317
Type: osv

## Details
OP-TEE is a Trusted Execution Environment (TEE) designed as companion to a non-secure Linux kernel running on Arm; Cortex-A cores using the TrustZone technology. In versions 3.13.0 through 4.10.0, missing checks in `entry_get_attribute_value()`  in `ta/pkcs11/src/object.c` can lead to out-of-bounds read from the PKCS#11 TA heap or a crash. When chained with the OOB read, the PKCS#11 TA function `PKCS11_CMD_GET_ATTRIBUTE_VALUE`  or `entry_get_attribute_value()` can, with a bad template parameter, be tricked into reading at most 7 bytes beyond the end of the template buffer and writing beyond the end of the template buffer with the content of an attribute value of a PKCS#11 object. Commits e031c4e562023fd9f199e39fd2e85797e4cbdca9, 16926d5a46934c46e6656246b4fc18385a246900, and 149e8d7ecc4ef8bb00ab4a37fd2ccede6d79e1ca contain patches and are anticipated to be part of version 4.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33317.json
- https://github.com/OP-TEE/optee_os/security/advisories/GHSA-8cqw-mg7v-c9p9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33317
- https://github.com/OP-TEE/optee_os/commit/149e8d7ecc4ef8bb00ab4a37fd2ccede6d79e1ca
- https://github.com/OP-TEE/optee_os/commit/16926d5a46934c46e6656246b4fc18385a246900
- https://github.com/OP-TEE/optee_os/commit/e031c4e562023fd9f199e39fd2e85797e4cbdca9
