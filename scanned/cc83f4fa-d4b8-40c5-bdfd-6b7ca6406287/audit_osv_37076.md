# [M] Wazuh: Pre-auth stack-based buffer overflow in wazuh-remoted print_hex_string() due to signed char promotion on x86_64

## Summary
Severity: Medium
Advisory: CVE-2026-28221
Aliases: GHSA-q9vv-7w4c-f4cm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-28221
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From version 4.8.0 to before version 4.14.4, a stack-based buffer overflow exists in print_hex_string() in wazuh-remoted. The bug is triggered when formatting attacker-controlled bytes using sprintf(dst_buf + 2*i, "%.2x", src_buf[i]) on platforms where char is treated as signed and the compiled code sign-extends bytes before the variadic call. For input bytes such as 0xFF, the formatting can emit "ffffffff" (8 chars) instead of "ff" (2 chars), causing an out-of-bounds write past a fixed 2049-byte stack buffer. The vulnerable path is reachable remotely prior to any agent authentication/registration logic via TCP/1514 when an oversized length prefix causes the “unexpected message (hex)” diagnostic path to run. Additionally, the same unauthenticated oversized-message diagnostic path logs an attacker-controlled hex dump to /var/ossec/logs/ossec.log for each trigger, allowing remote log amplification that can degrade monitoring fidelity and consume disk/I/O. This log amplification is reachable even without triggering the sign-extension overflow (e.g., using bytes < 0x80). This issue has been patched in version 4.14.4.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28221.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-q9vv-7w4c-f4cm
- https://nvd.nist.gov/vuln/detail/CVE-2026-28221
