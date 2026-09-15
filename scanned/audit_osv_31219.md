# [H] Incorrect Address Range Calculations

## Summary
Severity: High
Advisory: CVE-2024-6287
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-6287
Type: osv

## Details
Incorrect Calculation vulnerability in Renesas arm-trusted-firmware allows Local Execution of Code.


When checking whether a new image invades/overlaps with a previously loaded image the code neglects to consider a few cases. that could An attacker to bypass memory range restriction and overwrite an already loaded image partly or completely, which could result in code execution and bypass of secure boot.

## References
- https://github.com/renesas-rcar/arm-trusted-firmware/
- https://asrg.io/security-advisories/cve-2024-6287/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6287.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6287
- https://github.com/renesas-rcar/arm-trusted-firmware/commit/954d488a9798f8fda675c6b57c571b469b298f04
