# [M] Meshtastic crashes via an unimplemented routing module reply

## Summary
Severity: Medium
Advisory: CVE-2025-24798
Aliases: GHSA-4q84-546j-3mf5
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-24798
Type: osv

## Details
Meshtastic is an open source mesh networking solution. From 1.2.1 until 2.6.2, a packet sent to the routing module that contains want_response==true causes a crash. This can lead to a degradation of service for nodes within range of a malicious sender, or via MQTT if downlink is enabled. This vulnerability is fixed in 2.6.2.

## References
- https://github.com/meshtastic/firmware/blob/cdcbf4c61550e45c125e17a20aff4275e9389655/src/modules/RoutingModule.cpp#L44-L48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24798.json
- https://github.com/meshtastic/firmware/security/advisories/GHSA-4q84-546j-3mf5
- https://nvd.nist.gov/vuln/detail/CVE-2025-24798
- https://github.com/meshtastic/firmware/commit/dc100e4d3e3dfbf58d3ead8141a49cddb0cbdc19
