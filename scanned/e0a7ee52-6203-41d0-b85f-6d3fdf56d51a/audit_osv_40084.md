# [M] FreeSWITCH includes a vulnerable function, PREFIX(prologTok)() from libexpat

## Summary
Severity: Medium
Advisory: CVE-2026-49472
Aliases: GHSA-4jm3-xpcm-mwwq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49472
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.0, FreeSWITCH includes a vulnerable function, PREFIX(prologTok)(), in libs/xmlrpc-c/lib/expat/xmltok/xmltok_impl.c, which was cloned from an outdated and vulnerable version in libexpat/libexpat. The function did not receive the corresponding security patch. This issue has been patched in version 1.11.0.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49472.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-4jm3-xpcm-mwwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-49472
