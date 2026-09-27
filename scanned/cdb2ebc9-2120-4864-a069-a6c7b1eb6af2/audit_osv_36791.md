# [M] Wazuh Database Synchronization Vulnerable to Stack-based Buffer Overflow via snprintf Integer Underflow

## Summary
Severity: Medium
Advisory: CVE-2026-25772
Aliases: GHSA-h7vp-j34v-h6j5
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-25772
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. Starting in version 4.4.0 and prior to version 4.14.3, a stack-based buffer overflow vulnerability exists in the Wazuh Database synchronization module (`wdb_delta_event.c`). The SQL query construction logic allows for an integer underflow when calculating the remaining buffer size. This occurs because the code incorrectly aggregates the return value of `snprintf`. If a specific database synchronization payload exceeds the size of the query buffer (2048 bytes), the size calculation wraps around to a massive integer, effectively removing bounds checking for subsequent writes. This allows an attacker to corrupt the stack, leading to a Denial of Service (DoS) or potentially RCE. Version 4.14.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25772.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-h7vp-j34v-h6j5
- https://nvd.nist.gov/vuln/detail/CVE-2026-25772
