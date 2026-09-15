# [C] xrdp: lib_palette_update Heap Buffer Overflow & RCE

## Summary
Severity: Critical
Advisory: CVE-2026-41252
Aliases: GHSA-w5vg-6qmv-j63j
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-41252
Type: osv

## Details
xrdp is an open source RDP server. Versions 0.10.6 and prior contain a missing bounds check in xrdp, which allows a heap-based buffer overflow when operating in vnc-any mode. The issue occurs during the handling of RFB protocol color map messages from a VNC server, where incoming color indices are not properly validated. A malicious VNC server can exploit this flaw by sending crafted messages with out-of-range values, leading to an out-of-bounds write on the heap. This memory corruption can result in a denial of service (DoS) or potentially allow remote code execution (RCE) prior to authentication. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41252.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-w5vg-6qmv-j63j
- https://nvd.nist.gov/vuln/detail/CVE-2026-41252
