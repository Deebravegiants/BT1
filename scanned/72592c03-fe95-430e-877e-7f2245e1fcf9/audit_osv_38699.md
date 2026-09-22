# [M] Wazuh: Multiple Heap-based NULL WRITE Buffer Underflows in parse_uname_string()

## Summary
Severity: Medium
Advisory: CVE-2026-41499
Aliases: GHSA-qvqj-p8mm-r7h3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-41499
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From version 4.0.0 to before version 4.14.4, multiple heap-based out-of-bounds WRITE vulnerabilities exist in parse_uname_string() (remoted_op.c). This function processes OS identification data from agents and contains a dangerous code pattern that appears in 4 locations within the same function: writing to strlen(ptr) - 1 without checking for empty strings. When the string is empty, strlen() returns 0, and 0 - 1 wraps to SIZE_MAX due to unsigned integer underflow. Due to pointer arithmetic wrapping, SIZE_MAX effectively becomes -1, causing a write exactly 1 byte before the allocated buffer. This corrupts heap metadata (e.g., the chunk size field in glibc malloc), leading to heap corruption. This issue has been patched in version 4.14.4.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41499.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-qvqj-p8mm-r7h3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41499
