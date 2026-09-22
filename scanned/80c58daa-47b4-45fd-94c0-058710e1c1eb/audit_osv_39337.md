# [C] Quark Drive (quark-auto-save) < 0.8.5 Mass Assignment via POST /update

## Summary
Severity: Critical
Advisory: CVE-2026-45229
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-45229
Type: osv

## Details
Quark Drive before 0.8.5 contains a mass assignment vulnerability in the POST /update endpoint that allows authenticated attackers to overwrite administrator credentials by posting an arbitrary webui object to the config_data dictionary. Attackers can exploit insufficient deny-list filtering to permanently replace stored login credentials, lock out legitimate administrators, and gain persistent access to all configured tasks, cloud tokens, and notification services.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45229.json
- https://github.com/Cp0204/quark-auto-save/releases/tag/v0.8.5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45229
- https://www.vulncheck.com/advisories/quark-drive-mass-assignment-via-post-update
- https://github.com/Cp0204/quark-auto-save/commit/ea8377a596446291953dbe36e2d119d85bcd865b
- https://github.com/Cp0204/quark-auto-save
