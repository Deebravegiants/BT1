# [M] Failure to check for packets from the broadcast address allows potential DDoS amplification attack in Meshtastic firmware

## Summary
Severity: Medium
Advisory: CVE-2024-51500
Aliases: GHSA-xfmq-5j3j-vgv8
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-11-04
Source: https://osv.dev/vulnerability/CVE-2024-51500
Type: osv

## Details
Meshtastic firmware is a device firmware for the Meshtastic project. The Meshtastic firmware does not check for packets claiming to be from the special broadcast address (0xFFFFFFFF) which could result in unexpected behavior and potential for DDoS attacks on the network. A malicious actor could craft a packet to be from that address which would result in an amplification of this one message into every node on the network sending multiple messages. Such an attack could result in degraded network performance for all users as the available bandwidth is consumed. This issue has been addressed in release version 2.5.6. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51500.json
- https://github.com/meshtastic/firmware/security/advisories/GHSA-xfmq-5j3j-vgv8
- https://nvd.nist.gov/vuln/detail/CVE-2024-51500
