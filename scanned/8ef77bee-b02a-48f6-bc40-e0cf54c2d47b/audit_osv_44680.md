# [H] MOOS core-moos through 10.4.0 Off-by-One Buffer Overflow in Serial Telegram Handling

## Summary
Severity: High
Advisory: CVE-2026-85454
CVSS: 7.5 (CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85454
Type: osv

## Details
MOOS core-moos through 10.4.0 contains a buffer overflow vulnerability in CMOOSSerialPort::GetTelegram() that writes a NUL terminator one byte past the serial telegram stack buffer. Attackers controlling the serial line can send a full-length telegram to trigger the off-by-one write, corrupting the stack and potentially enabling code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85454.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85454
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-off-by-one-buffer-overflow-in-serial-telegram-handling
- https://github.com/themoos/core-moos/commit/befb04df2039d0080715ea35f56268092db4ec0f
- https://github.com/themoos/core-moos/pull/73
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/Utils/MOOSSerialPort.cpp#L595
