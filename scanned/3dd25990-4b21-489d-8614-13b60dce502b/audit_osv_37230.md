# [H] CVE-2026-29972

## Summary
Severity: High
Advisory: CVE-2026-29972
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-29972
Type: osv

## Details
nanoMODBUS through v1.22.0 has a stack-based buffer overflow in recv_read_registers_res() in nanomodbus.c. When a client calls nmbs_read_holding_registers() or nmbs_read_input_registers(), the library writes register data from the server response to the caller-provided buffer based on the response's byte_count field before validating that byte_count matches the requested quantity. A malicious Modbus TCP server can send a response with byte_count=250 (125 registers) regardless of the requested quantity, causing up to 248 bytes of attacker-controlled data to overflow the buffer, potentially allowing remote code execution.

## References
- https://gist.github.com/dwilliams27/a4e26fe747c8561d608f7549804bd85f
- https://github.com/debevv/nanoMODBUS/blob/master/nanomodbus.c#L580-L615
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29972.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29972
- https://github.com/debevv/nanoMODBUS
