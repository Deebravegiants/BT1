# [M] Uninitialized TRNG used for ECDSA after EM2/EM3 sleep for VSE devices

## Summary
Severity: Medium
Advisory: CVE-2024-22473
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-22473
Type: osv

## Details
TRNG is used before initialization by ECDSA signing driver when exiting EM2/EM3 on Virtual Secure Vault (VSE) devices. This defect may allow Signature Spoofing by Key Recreation.This issue affects Gecko SDK through v4.4.0.

## References
- https://community.silabs.com/068Vm000001FrjT
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22473.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22473
- https://github.com/SiliconLabs/gecko_sdk/releases
