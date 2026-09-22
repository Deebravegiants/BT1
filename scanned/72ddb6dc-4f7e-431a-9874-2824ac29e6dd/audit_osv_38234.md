# [H] pyLoad has Improper Neutralization of Special Elements used in an OS Command

## Summary
Severity: High
Advisory: CVE-2026-35463
Aliases: GHSA-w48f-wwwf-f5fr, PYSEC-2026-2267
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35463
Type: osv

## Details
pyLoad is a free and open-source download manager written in Python. In 0.5.0b3.dev96 and earlier, the ADMIN_ONLY_OPTIONS protection mechanism restricts security-critical configuration values (reconnect scripts, SSL certs, proxy credentials) to admin-only access. However, this protection is only applied to core config options, not to plugin config options. The AntiVirus plugin stores an executable path (avfile) in its config, which is passed directly to subprocess.Popen(). A non-admin user with SETTINGS permission can change this path to achieve remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35463.json
- https://github.com/pyload/pyload/security/advisories/GHSA-w48f-wwwf-f5fr
- https://nvd.nist.gov/vuln/detail/CVE-2026-35463
- https://github.com/pyload/pyload/commit/c4cf995a2803bdbe388addfc2b0f323277efc0e1
