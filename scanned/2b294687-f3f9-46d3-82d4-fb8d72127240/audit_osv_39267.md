# [C] Unauthenticated RCE via Python Config File Injection in SaveConfigFile() (Path)

## Summary
Severity: Critical
Advisory: CVE-2026-44887
Aliases: GHSA-r59g-5wf9-f7vv
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-44887
Type: osv

## Details
Pi.Alert is a WIFI / LAN intruder detector with web service monitoring. Prior to 2026-05-07, Pi.Alert's web-based configuration editor allows arbitrary Python code to be injected into pialert.conf. Since the background scan daemon loads this file via Python's exec(), injected code executes as the daemon process. With web protection disabled (the default configuration), no authentication is required, making this an unauthenticated Remote Code Execution vulnerability. This vulnerability is fixed in 2026-05-07.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44887.json
- https://github.com/leiweibau/Pi.Alert/security/advisories/GHSA-r59g-5wf9-f7vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44887
