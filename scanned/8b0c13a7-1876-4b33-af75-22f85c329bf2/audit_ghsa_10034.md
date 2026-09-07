# [H] Weblate: Privilege escalation in the user API endpoint

## Summary
Severity: High
Advisory: GHSA-3382-gw9x-477v
CVE: CVE-2026-34393
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-3382-gw9x-477v
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.17

## Details
### Impact

The user patching API endpoint didn't properly limit the scope of edits.

### Patches
* https://github.com/WeblateOrg/weblate/pull/18687


### References
Thanks to @tikket1 and @DavidCarliez for reporting this via GitHub. We received two individual reports for this.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-3382-gw9x-477v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34393
- https://github.com/WeblateOrg/weblate/pull/18687
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2026-155.yaml
