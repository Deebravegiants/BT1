# [H] TDengine has an integer underflow in uvConnMayGetUserInfo() allows unauthenticated remote crash (DoS)

## Summary
Severity: High
Advisory: CVE-2026-42542
Aliases: GHSA-vg95-j2hf-hvjx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-42542
Type: osv

## Details
TDengine is an open source, time-series database optimized for Internet of Things devices. In versions 3.4.0.0 through 3.4.1.5, an unauthenticated remote attacker can crash the taosd server process by sending a single crafted RPC packet. No credentials or prior session state are required. Version 3.4.1.6 fixes the issue.

## References
- https://github.com/taosdata/TDengine/releases/tag/ver-3.4.1.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42542.json
- https://github.com/taosdata/TDengine/security/advisories/GHSA-vg95-j2hf-hvjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-42542
