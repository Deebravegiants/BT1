# [M] FreeRDP: Denial of service through ADPCM frame size calculation

## Summary
Severity: Medium
Advisory: CVE-2026-63117
Aliases: GHSA-v64m-xxfw-hrv6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-63117
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.28.0, an authenticated RDP client can advertise DVI ADPCM with nBlockAlign equal to 8 and nChannels equal to 2 to make the `bs` calculation in rdpsnd_server_select_format in channels/rdpsnd/server/rdpsnd_main.c equal zero. The subsequent out_frames modulo `bs` operation raises SIGFPE and terminates the server-side rdpsnd channel process. This vulnerability fixed in 3.28.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63117.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-v64m-xxfw-hrv6
- https://nvd.nist.gov/vuln/detail/CVE-2026-63117
- https://github.com/FreeRDP/FreeRDP/commit/b78fc0b138fe8f08a8b102e193ffb32986f4449a
- https://github.com/FreeRDP/FreeRDP/pull/12980
