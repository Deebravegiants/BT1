# [M] CVE-2022-47549

## Summary
Severity: Medium
Advisory: CVE-2022-47549
Aliases: GHSA-r64m-h886-hw6g
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-19
Source: https://osv.dev/vulnerability/CVE-2022-47549
Type: osv

## Details
An unprotected memory-access operation in optee_os in TrustedFirmware Open Portable Trusted Execution Environment (OP-TEE) before 3.20 allows a physically proximate adversary to bypass signature verification and install malicious trusted applications via electromagnetic fault injections.

## References
- https://people.linaro.org/~joakim.bech/reports/Breaking_cross-world_isolation_on_ARM_TrustZone_through_EM_faults_coredumps_and_UUID_confusion.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47549.json
- https://github.com/OP-TEE/optee_os/security/advisories/GHSA-r64m-h886-hw6g
- https://nvd.nist.gov/vuln/detail/CVE-2022-47549
