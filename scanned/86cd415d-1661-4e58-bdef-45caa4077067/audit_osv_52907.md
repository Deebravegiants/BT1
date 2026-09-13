# [M] CVE-2022-21505

## Summary
Severity: Medium
Advisory: CVE-2022-21505
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2022-21505
Type: osv

## Details
In the linux kernel, if IMA appraisal is used with the "ima_appraise=log" boot param, lockdown can be defeated with kexec on any machine when Secure Boot is disabled or unavailable. IMA prevents setting "ima_appraise=log" from the boot param when Secure Boot is enabled, but this does not cover cases where lockdown is used without Secure Boot. CVSS 3.1 Base Score 6.7 (Confidentiality, Integrity, Availability impacts). CVSS Vector: (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H).

## References
- https://git.kernel.org/linus/543ce63b664e2c2f9533d089a4664b559c3e6b5b
- https://linux.oracle.com/cve/CVE-2022-21505.html
