# [H] Harbor fails to validate the user permissions when updating tag retention policies

## Summary
Severity: High
Advisory: GHSA-3637-v6vq-xqqw
CVE: CVE-2022-31670
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-3637-v6vq-xqqw
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.0.0 <1.10.13
- Go: `github.com/goharbor/harbor` — affected >=2.0.0 <2.4.3
- Go: `github.com/goharbor/harbor` — affected >=2.5.0 <2.5.2

## Details
### Impact
 Harbor fails to validate the user permissions when updating tag retention policies. API call:

  PUT /retentions/{id}

By sending a request to update a tag retention policy with an id that belongs to a project
that the currently authenticated user doesn’t have access to, the attacker could modify
tag retention policies configured in other projects.

### Patches
This and similar issues are fixed in Harbor v2.5.2 and later. Please upgrade as soon as possible.

### Workarounds
There are no workarounds available.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Harbor GitHub repository](https://github.com/goharbor/harbor)

### Credits
Thanks to [Gal Goldstein](https://www.linkedin.com/in/gal-goldshtein/) and [Daniel Abeles](https://www.linkedin.com/in/daniel-abeles/) from [Oxeye Security](https://www.oxeye.io/) for reporting this issue.

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-3637-v6vq-xqqw
- https://nvd.nist.gov/vuln/detail/CVE-2022-31670
- https://github.com/goharbor/harbor
