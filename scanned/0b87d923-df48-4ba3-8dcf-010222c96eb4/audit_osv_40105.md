# [C] FreeSWITCH: Pre-authentication heap buffer overflow in `mod_verto` HTTP POST body read

## Summary
Severity: Critical
Advisory: CVE-2026-49841
Aliases: GHSA-wfrq-qvg2-f88f
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49841
Type: osv

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.11.1, the mod_verto HTTP request handler allocates a fixed 2 MiB buffer for a POST application/x-www-form-urlencoded body but accepts Content-Length up to just under 10 MiB. The body-read loop is bounded by Content-Length rather than the buffer size, producing an attacker-controlled heap overflow of up to ~8 MiB -- before the HTTP basic-auth check runs. This issue has been patched in version 1.11.1.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49841.json
- https://github.com/signalwire/freeswitch/security/advisories/GHSA-wfrq-qvg2-f88f
- https://nvd.nist.gov/vuln/detail/CVE-2026-49841
