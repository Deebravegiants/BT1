# [H] Integer overflow in Silicon Labs Gecko Bootloader leads to unbounded memory access

## Summary
Severity: High
Advisory: CVE-2023-3487
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-3487
Type: osv

## Details
An integer overflow in Silicon Labs Gecko Bootloader version 4.3.1 and earlier allows unbounded memory access when reading from or writing to storage slots.

## References
- https://community.silabs.com/s/contentdocument/0698Y00000ZmXqLQAV
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3487.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3487
- https://github.com/SiliconLabs/gecko_sdk/releases
