# [H] CVE-2021-36133

## Summary
Severity: High
Advisory: CVE-2021-36133
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-12-07
Source: https://osv.dev/vulnerability/CVE-2021-36133
Type: osv

## Details
The OPTEE-OS CSU driver for NXP i.MX SoC devices lacks security access configuration for several models, resulting in TrustZone bypass because the NonSecure World can perform arbitrary memory read/write operations on Secure World memory. This involves a DMA capable peripheral.

## References
- https://github.com/f-secure-foundry/advisories/blob/master/Security_Advisory-Ref_FSC-HWSEC-VR2021-0001-OP-TEE_TrustZone_bypass.txt
