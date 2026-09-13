# [H] CVE-2026-27856

## Summary
Severity: High
Advisory: CVE-2026-27856
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-27856
Type: osv

## Details
Doveadm credentials are verified using direct comparison which is susceptible to timing oracle attack. An attacker can use this to determine the configured credentials. Figuring out the credential will lead into full access to the affected component. Limit access to the doveadm http service port, install fixed version. No publicly available exploits are known.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27856.json
- https://access.redhat.com/errata/RHSA-2026:26564
- https://access.redhat.com/security/cve/CVE-2026-27856
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27856.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27856
- https://bugzilla.redhat.com/show_bug.cgi?id=2452171
