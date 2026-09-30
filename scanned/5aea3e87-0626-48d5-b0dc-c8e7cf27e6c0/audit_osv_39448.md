# [H] Suricata defrag: missing address-family check can lead to remote crash

## Summary
Severity: High
Advisory: CVE-2026-45762
Aliases: GHSA-gv2j-f6jv-3878
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45762
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, Suricata's IP defragmentation tracker lookup did not verify that an existing tracker used the same IP address family as the packet being processed. Under crafted fragmented IPv4/IPv6 traffic, an IPv6 fragment could be associated with an IPv4 defragmentation tracker. This can lead to a remote packet-triggered crash and denial of service when Suricata performs the relevant defragmentation. Versions 7.0.16 and 8.0.5 contain a fix. As a workaround, if using Suricata as an IDS with AF_PACKET, enabling AF_PACKET's `defrag` option may prevent Suricata from seeing such fragmented packets.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8510
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45762.json
- https://github.com/OISF/suricata/security/advisories/GHSA-gv2j-f6jv-3878
- https://nvd.nist.gov/vuln/detail/CVE-2026-45762
