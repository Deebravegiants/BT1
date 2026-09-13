# [M] UEFI Shell accessible in AAVMF with Secure Boot enabled on Ubuntu

## Summary
Severity: Medium
Advisory: CVE-2025-2486
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H/E:U)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-2486
Type: osv

## Details
The Ubuntu edk2 UEFI firmware packages accidentally allowed the UEFI Shell to be accessed in Secure Boot environments, possibly allowing bypass of Secure Boot constraints. Versions 2024.05-2ubuntu0.3 and 2024.02-2ubuntu0.3 disable the Shell. Some previous versions inserted a secure-boot-based decision to continue running inside the Shell itself, which is believed to be sufficient to enforce Secure Boot restrictions. This is an additional repair on top of the incomplete fix for CVE-2023-48733.

## References
- https://bugs.launchpad.net/ubuntu/+source/edk2/+bug/2101797
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2486.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2486
