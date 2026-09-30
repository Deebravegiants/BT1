# [C] OpenRGB: local and remote system compromise via arbitrary file write using attacker controlled strings

## Summary
Severity: Critical
Advisory: CVE-2026-59683
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-59683
Type: osv

## Details
The OpenRGB network protocol allows to write attacker controlled strings into arbitrary file system paths (extension of CVE-2026-59682). This allows either a full system compromise from local or remote (if the daemon is running as root) or a full account takeover (if the daemon is running in user context).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59683.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59683
- https://bugzilla.suse.com/show_bug.cgi?id=1274007
- https://gitlab.com/CalcProgrammer1/OpenRGB/-/commit/d2dd9dcc7369e78f47d01ace19af3750cd89ae66
- https://gitlab.com/CalcProgrammer1/OpenRGB
