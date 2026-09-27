# [C] Meshtastic incorrectly hands malformed packets leads to controlled buffer overflow

## Summary
Severity: Critical
Advisory: CVE-2025-24797
Aliases: GHSA-33hw-xhfh-944r
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-24797
Type: osv

## Details
Meshtastic is an open source mesh networking solution. A fault in the handling of mesh packets containing invalid protobuf data can result in an attacker-controlled buffer overflow, allowing an attacker to hijack execution flow, potentially resulting in remote code execution. This attack does not require authentication or user interaction, as long as the target device rebroadcasts packets on the default channel. This vulnerability fixed in 2.6.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24797.json
- https://github.com/meshtastic/firmware/security/advisories/GHSA-33hw-xhfh-944r
- https://nvd.nist.gov/vuln/detail/CVE-2025-24797
