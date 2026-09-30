# [M] CVE-2020-15107

## Summary
Severity: Medium
Advisory: CVE-2020-15107
Aliases: GHSA-7wjx-wcwg-w999
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:N/I:H/A:N)
Published: 2020-07-15
Source: https://osv.dev/vulnerability/CVE-2020-15107
Type: osv

## Details
In openenclave before 0.10.0, enclaves that use x87 FPU operations are vulnerable to tampering by a malicious host application. By violating the Linux System V Application Binary Interface (ABI) for such operations, a host app can compromise the execution integrity of some x87 FPU operations in an enclave. Depending on the FPU control configuration of the enclave app and whether the operations are used in secret-dependent execution paths, this vulnerability may also be used to mount a side-channel attack on the enclave. This has been fixed in 0.10.0 and the current master branch. Users will need to recompile their applications against the patched libraries to be protected from this vulnerability.

## References
- https://github.com/openenclave/openenclave/security/advisories/GHSA-7wjx-wcwg-w999
