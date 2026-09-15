# [H] MacCMS10 - Incomplete Function Blacklist in Template Editor Enables Authenticated RCE

## Summary
Severity: High
Advisory: CVE-2026-71232
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71232
Type: osv

## Details
MacCMS10's admin template editor (application/admin/controller/Template.php) blocks dangerous PHP functions in template content via a blacklist regex, but the blacklist omitted exec, passthru, popen, show_source, create_function, register_shutdown_function, register_tick_function, and error_log.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71232.json
- https://github.com/magicblack/maccms10/commit/71ad3bb29570e110d8e973acff68040a3050ddf0
- https://nvd.nist.gov/vuln/detail/CVE-2026-71232
