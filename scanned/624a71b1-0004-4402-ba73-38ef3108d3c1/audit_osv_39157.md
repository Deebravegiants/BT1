# [M] Wazuh: Stack Out-of-Bounds Write in remoted Decompression Path

## Summary
Severity: Medium
Advisory: CVE-2026-44254
Aliases: GHSA-9wm4-fp6c-hqgq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-44254
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 1.0.0 until 4.14.6 and 5.0.0-beta2, HandleSecureMessage() in src/remoted/secure.c passes a pointer inside its stack buffer to ReadSecMSG(), and src/os_crypto/shared/msgs.c decompresses up to OS_MAXSTR bytes at that offset. For an encrypted agent message on TCP port 1514 that expands to 65,536 bytes, os_zlib_uncompress() writes a terminating null byte beyond the end of the destination buffer. The resulting stack out-of-bounds write in the root-level remoted daemon can crash message processing and disrupt agent communications. This issue is fixed in versions 4.14.6 and 5.0.0-beta2.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44254.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-9wm4-fp6c-hqgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44254
- https://github.com/wazuh/wazuh/commit/96772487fbdecd43cc83e284ee7aeb45e3cfcd96
- https://github.com/wazuh/wazuh/pull/35773
