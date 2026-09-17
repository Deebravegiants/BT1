# [H] Ineffective size check due to assert() and buffer overflow in RIOT

## Summary
Severity: High
Advisory: CVE-2024-32018
Aliases: GHSA-899m-q6pp-hmp3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-32018
Type: osv

## Details
RIOT is a real-time multi-threading operating system that supports a range of devices that are typically 8-bit, 16-bit and 32-bit microcontrollers. Most codebases define assertion macros which compile to a no-op on non-debug builds. If assertions are the only line of defense against untrusted input, the software may be exposed to attacks that leverage the lack of proper input checks. In detail, in the `nimble_scanlist_update()` function below, `len` is checked in an assertion and subsequently used in a call to `memcpy()`. If an attacker is able to provide a larger `len` value while assertions are compiled-out, they can write past the end of the fixed-length `e->ad` buffer. If the unchecked input above is attacker-controlled and crosses a security boundary, the impact of the buffer overflow vulnerability could range from denial of service to arbitrary code execution. This issue has not yet been patched. Users are advised to add manual `len` checking.

## References
- http://seclists.org/fulldisclosure/2024/May/7
- http://www.openwall.com/lists/oss-security/2024/05/07/3
- https://github.com/RIOT-OS/RIOT/blob/master/pkg/nimble/scanlist/nimble_scanlist.c#L74-L87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32018.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-899m-q6pp-hmp3
- https://nvd.nist.gov/vuln/detail/CVE-2024-32018
