# [H] CVE-2022-28735

## Summary
Severity: High
Advisory: CVE-2022-28735
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2022-28735
Type: osv

## Details
The GRUB2's shim_lock verifier allows non-kernel files to be loaded on shim-powered secure boot systems. Allowing such files to be loaded may lead to unverified code and modules to be loaded in GRUB2 breaking the secure boot trust-chain.

## References
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-28735
- https://security.netapp.com/advisory/ntap-20230825-0002/
- https://www.openwall.com/lists/oss-security/2022/06/07/5
