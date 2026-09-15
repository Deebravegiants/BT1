# [H] Velociraptor Analyst overwrites live built-in artifacts through verify()

## Summary
Severity: High
Advisory: CVE-2026-19200
CVSS: 8.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-19200
Type: osv

## Details
The Velociraptor verify() VQL function allows a user to verify an artifact for syntatic and other issues. Due to an implementation fault in this VQL function, the global artifact repository is used which allows callers to overwrite existing artifacts without the required permissions.  The attacker need only have the NOTEBOOK_EDIT permission (e.g. an analyst role) to be able to call this function.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-19200/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19200.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19200
- https://github.com/Velocidex/velociraptor/pull/4962
