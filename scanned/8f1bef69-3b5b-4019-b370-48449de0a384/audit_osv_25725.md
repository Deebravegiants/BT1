# [C] Unvalidated input in Silicon Labs TrustZone implementation leads to accessing Trusted memory region

## Summary
Severity: Critical
Advisory: CVE-2023-4280
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-4280
Type: osv

## Details
An unvalidated input in Silicon Labs TrustZone implementation in v4.3.x and earlier of the Gecko SDK allows an attacker to access the trusted region of memory from the untrusted region.

## References
- https://community.silabs.com/069Vm0000004NinIAE
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4280.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4280
- https://github.com/SiliconLabs/gecko_sdk
