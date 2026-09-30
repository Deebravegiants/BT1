# [H] CVE-2024-34244

## Summary
Severity: High
Advisory: CVE-2024-34244
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-08
Source: https://osv.dev/vulnerability/CVE-2024-34244
Type: osv

## Details
libmodbus v3.1.10 is vulnerable to Buffer Overflow via the modbus_write_bits function. This issue can be triggered when the function is fed with specially crafted input, which leads to out-of-bounds read and can potentially cause a crash or other unintended behaviors.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34244.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34244
- https://github.com/stephane/libmodbus/issues/743
