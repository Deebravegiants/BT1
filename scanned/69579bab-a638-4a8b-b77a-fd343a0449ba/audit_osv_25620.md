# [C] Unvalidated input in Silicon Labs PSA Attestation service leads to secure memory access from non-secure memory

## Summary
Severity: Critical
Advisory: CVE-2023-4020
CVSS: 9.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-12-15
Source: https://osv.dev/vulnerability/CVE-2023-4020
Type: osv

## Details
An unvalidated input in a library function responsible for communicating between secure and non-secure memory in Silicon Labs TrustZone implementation allows reading/writing of memory in the secure region of memory from the non-secure region of memory.

## References
- https://community.silabs.com/069Vm0000004b95IAA
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4020.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4020
- https://github.com/SiliconLabs/gecko_sdk/releases
