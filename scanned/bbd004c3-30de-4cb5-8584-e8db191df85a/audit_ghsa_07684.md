# [M] Weblate has an argument injection in management console

## Summary
Severity: Medium
Advisory: GHSA-33fm-6gp7-4p47
CVE: CVE-2026-24126
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-33fm-6gp7-4p47
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.16.0

## Details
### Impact
The SSH management console did not validate the passed input while adding the SSH host key, which could lead to an argument injection to `ssh-add`.

### Patches
* https://github.com/WeblateOrg/weblate/pull/17722

### Workarounds
Properly limit access to the management console.

### References
This issue was reported to us by [alexb_616](https://hackerone.com/alexb_616) via HackerOne.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-33fm-6gp7-4p47
- https://nvd.nist.gov/vuln/detail/CVE-2026-24126
- https://github.com/WeblateOrg/weblate/pull/17722
- https://github.com/WeblateOrg/weblate/commit/78773cc141ce0a97900c11341e6cf856451395fd
- https://github.com/WeblateOrg/weblate
