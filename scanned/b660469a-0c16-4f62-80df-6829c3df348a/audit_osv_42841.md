# [C] OP-TEE OS 4.10.0 Use-After-Free via Trusted Application Loader TA_FLAG_CONCURRENT

## Summary
Severity: Critical
Advisory: CVE-2026-71968
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-71968
Type: osv

## Details
OP-TEE OS through 4.10.0, fixed in commit 8794043, contains a use-after-free vulnerability in the Trusted Application loader that allows attackers with the ability to load a signed Trusted Application to corrupt secure-world kernel memory by setting the TA_FLAG_CONCURRENT flag in a user TA signed header. Attackers can cause two concurrent sessions to operate on the same shared context without locking, corrupting the uctx->vm_info.regions list during memref parameter mapping and unmapping to free vm_region nodes still in use, resulting in a use-after-free in S-EL1 secure-world kernel memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71968.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71968
- https://www.vulncheck.com/advisories/op-tee-os-use-after-free-via-trusted-application-loader-ta-flag-concurrent
- https://github.com/OP-TEE/optee_os/pull/7900
- https://github.com/OP-TEE/optee_os/commit/8794043c4065c26a2b8b1313794ba5ba5f06d296
- https://github.com/OP-TEE/optee_os
