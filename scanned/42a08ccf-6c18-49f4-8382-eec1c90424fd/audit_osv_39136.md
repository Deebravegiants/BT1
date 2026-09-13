# [H] xrdp: Channel Data Forwarding Fixed-Size Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-44178
Aliases: GHSA-hh7r-2rmq-q4g4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-44178
Type: osv

## Details
xrdp is an open source RDP server. Versions 0.10.6 and prior contain a heap-based buffer overflow vulnerability within the virtual channel forwarding mechanism. When forwarding data from a remote client to the internal channel server, the xrdp process utilizes a fixed-size buffer without adequate bounds checking on the incoming payload. An authenticated remote attacker can exploit this flaw by sending a specially crafted virtual channel message that exceeds the buffer capacity, leading to heap memory corruption. This may result in a denial of service or the execution of arbitrary code with the privileges of the xrdp process. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44178.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-hh7r-2rmq-q4g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44178
