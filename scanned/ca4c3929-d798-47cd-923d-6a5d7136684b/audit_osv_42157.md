# [C] FreeRDP before 3.28.0 Double-Free via selectedmonitors

## Summary
Severity: Critical
Advisory: CVE-2026-64621
Aliases: GHSA-f27x-frr8-j9hc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64621
Type: osv

## Details
FreeRDP before 3.28.0 (affected 3.x through 3.27.1) contains a double-free vulnerability in freerdp_client_rdp_file_apply_to_settings() (client/common/file.c) when parsing the selectedmonitors field of a .rdp connection file. The MonitorIds array is allocated through the settings object, and a raw non-owning pointer to it is freed on the strtoul error path without clearing settings->MonitorIds, leaving it dangling; at teardown freerdp_settings_free() frees the same buffer again. An attacker who convinces a victim to open a crafted .rdp file with oversized monitor tokens can trigger a size-controlled double-free in any FreeRDP CLI client (xfreerdp/sdl-freerdp/wlfreerdp) in the default configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64621.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-f27x-frr8-j9hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-64621
- https://www.vulncheck.com/advisories/freerdp-before-double-free-via-selectedmonitors
- https://github.com/FreeRDP/FreeRDP/commit/1f7a716d39b5605bb8a83b0c3c97a6ce386609ef
