# [H] xrdp: Pre-auth infinite loop via totalLength=0 in TS_SHARECONTROLHEADER

## Summary
Severity: High
Advisory: CVE-2026-54538
Aliases: GHSA-9j3q-9mvw-qv7j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-54538
Type: osv

## Details
xrdp is an open source RDP server. In versions 0.10.6 and prior, a n issue was discovered where the software fails to properly validate the totalLength field within the RDP protocol control header during packet reception. An unauthenticated remote attacker can exploit this vulnerability by sending a specially crafted packet that forces the xrdp process or thread into an infinite, CPU-bound loop. Because the internal pointer fails to advance and the deadlock prevention mechanism is bypassed for specific protocol data unit types, the process consumes excessive CPU resources indefinitely. This can render the xrdp service unavailable and potentially lead to system-wide resource exhaustion if multiple malicious connections are established. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54538.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-9j3q-9mvw-qv7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-54538
