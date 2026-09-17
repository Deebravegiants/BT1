# [M] OpenSIPS: Denial of Service in watcherinfo XML generation from oversized watcher URI

## Summary
Severity: Medium
Advisory: CVE-2026-45809
Aliases: GHSA-gx83-2gh8-7v56
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-45809
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Versions prior to 3.6.6 and 4.0.0-rc1 contain a denial of service vulnerability in the watcherinfo generation functionality. An attacker can create an oversized watcher entry by sending a SUBSCRIBE Event: presence request with a long From URI, and then trigger presence.winfo watcherinfo XML generation for the same presentity. OpenSIPS copies the stored watcher URI into a fixed-size stack buffer, overflowing it and crashing the process. A remote attacker can crash an OpenSIPS worker in deployments that expose handle_subscribe() and allow watcherinfo (presence.winfo) generation. The issue is configuration-dependent because the presence and presence_xml modules must be loaded and SUBSCRIBE routing must be reachable. This issue has been fixed in versions 3.6.6 and 4.0.0-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45809.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-gx83-2gh8-7v56
- https://nvd.nist.gov/vuln/detail/CVE-2026-45809
- https://github.com/OpenSIPS/opensips/commit/c5970d3ee25b457ad2d78fe6e9662a12dae577cd
- https://github.com/OpenSIPS/opensips/commit/dd86461b71ff4a4f5194205896ae5f48f144240d
