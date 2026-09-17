# [C] tufantunc ssh-mcp index.ts shell.write command injection

## Summary
Severity: Critical
Advisory: CVE-2026-7039
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-26
Source: https://osv.dev/vulnerability/CVE-2026-7039
Type: osv

## Details
A security vulnerability has been detected in tufantunc ssh-mcp up to 1.5.0. The affected element is the function shell.write of the file src/index.ts. Such manipulation of the argument Description leads to command injection. The attack must be carried out locally. The exploit has been disclosed publicly and may be used. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://github.com/tufantunc/ssh-mcp/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7039.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7039
- https://vuldb.com/submit/798528
- https://vuldb.com/vuln/359619
- https://github.com/tufantunc/ssh-mcp/issues/44
- https://vuldb.com/vuln/359619/cti
