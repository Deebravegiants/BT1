# [H] Wazuh: Pre-auth stack-buffer-overflow in compare_wazuh_versions reachable from wazuh-authd (TCP/1515) via crafted enrollment V: field

## Summary
Severity: High
Advisory: CVE-2026-45798
Aliases: GHSA-4fvp-jfc3-qr6r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-45798
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.5.0 until 4.14.6 and 5.0.0-beta2, compare_wazuh_versions() in src/shared/version_op.c copies the attacker-controlled enrollment V: field into a 10-byte stack buffer with strncpy() but does not explicitly terminate the buffer. The function is reachable before authentication through wazuh-authd on TCP port 1515 when anonymous TLS enrollment is enabled. A version string of at least nine non-null bytes can cause strchr() and strtok() to read beyond ver2 and can make strtok() write a null byte into adjacent stack memory, allowing a remote denial of service. This issue is fixed in versions 4.14.6 and 5.0.0-beta2.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45798.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-4fvp-jfc3-qr6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45798
- https://github.com/wazuh/wazuh/commit/b6aac379982d6144b8da38450cbea6c8dc15be44
- https://github.com/wazuh/wazuh/pull/36059
