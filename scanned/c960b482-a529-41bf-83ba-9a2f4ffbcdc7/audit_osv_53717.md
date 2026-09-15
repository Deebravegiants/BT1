# [M] CVE-2023-20584

## Summary
Severity: Medium
Advisory: CVE-2023-20584
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N)
Published: 2024-08-13
Source: https://osv.dev/vulnerability/CVE-2023-20584
Type: osv

## Details
IOMMU improperly handles certain special address
ranges with invalid device table entries (DTEs), which may allow an attacker
with privileges and a compromised Hypervisor to
induce DTE faults to bypass RMP checks in SEV-SNP, potentially leading to a
loss of guest integrity.

## References
- https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3003.html
