# [H] Arbitrary code execution for authenticated users in Icinga Web 2

## Summary
Severity: High
Advisory: CVE-2022-24715
Aliases: GHSA-v9mv-h52f-7g63
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-03-08
Source: https://osv.dev/vulnerability/CVE-2022-24715
Type: osv

## Details
Icinga Web 2 is an open source monitoring web interface, framework and command-line interface. Authenticated users, with access to the configuration, can create SSH resource files in unintended directories, leading to the execution of arbitrary code. This issue has been resolved in versions 2.8.6, 2.9.6 and 2.10 of Icinga Web 2. Users unable to upgrade should limit access to the Icinga Web 2 configuration.

## References
- http://packetstormsecurity.com/files/173516/Icinga-Web-2.10-Remote-Code-Execution.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24715.json
- https://github.com/Icinga/icingaweb2/security/advisories/GHSA-v9mv-h52f-7g63
- https://nvd.nist.gov/vuln/detail/CVE-2022-24715
- https://security.gentoo.org/glsa/202208-05
- https://github.com/Icinga/icingaweb2/commit/a06d915467ca943a4b406eb9587764b8ec34cafb
