# [H] Device crash via malformed MQTT packet when downlink is enabled in Meshtastic device firmware

## Summary
Severity: High
Advisory: CVE-2024-45038
Aliases: GHSA-3x3r-vw9f-pxq5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-27
Source: https://osv.dev/vulnerability/CVE-2024-45038
Type: osv

## Details
Meshtastic device firmware is a firmware for meshtastic devices to run an open source, off-grid, decentralized, mesh network built to run on affordable, low-power devices. Meshtastic device firmware is subject to a denial of serivce vulnerability in MQTT handling, fixed in version 2.4.1 of the Meshtastic firmware and on the Meshtastic public MQTT Broker. It's strongly suggested that all users of Meshtastic, particularly those that connect to a privately hosted MQTT server, update to this or a more recent stable version right away. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45038.json
- https://github.com/meshtastic/firmware/security/advisories/GHSA-3x3r-vw9f-pxq5
- https://nvd.nist.gov/vuln/detail/CVE-2024-45038
