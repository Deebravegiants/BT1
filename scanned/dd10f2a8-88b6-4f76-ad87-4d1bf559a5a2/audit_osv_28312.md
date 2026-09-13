# [H] Lack of size check and buffer overflow in RIOT

## Summary
Severity: High
Advisory: CVE-2024-31225
Aliases: GHSA-2572-7q7c-3965
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-31225
Type: osv

## Details
RIOT is a real-time multi-threading operating system that supports a range of devices that are typically 8-bit, 16-bit and 32-bit microcontrollers. The `_on_rd_init()` function does not implement a size check before copying data to the `_result_buf` static buffer. If an attacker can craft a long enough payload, they could cause a buffer overflow. If the unchecked input above is attacker-controlled and crosses a security boundary, the impact of the buffer overflow vulnerability could range from denial of service to arbitrary code execution. This issue has yet to be patched. Users are advised to add manual bounds checking.

## References
- http://seclists.org/fulldisclosure/2024/May/7
- http://www.openwall.com/lists/oss-security/2024/05/07/3
- https://github.com/RIOT-OS/RIOT/blob/master/sys/net/application_layer/cord/lc/cord_lc.c#L218
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31225.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-2572-7q7c-3965
- https://nvd.nist.gov/vuln/detail/CVE-2024-31225
