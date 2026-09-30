# [H] xrdp: lib_framebuffer_update Has Integer Overflow Heap Info Leak & ASLR Bypass

## Summary
Severity: High
Advisory: CVE-2026-41521
Aliases: GHSA-v8w6-pf78-9458
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-41521
Type: osv

## Details
xrdp is an open source RDP server. Versions 0.10.6 and prior contain an integer overflow vulnerability when processing screen update messages within the vnc-any connection mode. A malicious remote VNC server can send crafted image dimensions that cause an integer overflow during memory buffer size calculation, resulting in an undersized allocation. Subsequent processing of the incoming image data using the original oversized parameters leads to an out-of-bounds read. An unauthenticated remote attacker could exploit this flaw to disclose sensitive information from the heap memory or cause a denial of service (DoS) via a process crash. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41521.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-v8w6-pf78-9458
- https://nvd.nist.gov/vuln/detail/CVE-2026-41521
