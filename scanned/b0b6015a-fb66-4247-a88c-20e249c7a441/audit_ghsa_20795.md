# [M]  Harbor fails to validate the user permissions when updating a robot account

## Summary
Severity: Medium
Advisory: GHSA-xx9w-464f-7h6f
CVE: CVE-2022-31667
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-xx9w-464f-7h6f
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.0.0 <1.10.13
- Go: `github.com/goharbor/harbor` — affected >=2.0.0 <2.4.3
- Go: `github.com/goharbor/harbor` — affected >=2.5.0 <2.5.2

## Details
### Impact
Harbor fails to validate the user permissions when updating a robot account that
belongs to a project that the authenticated user doesn’t have access to. API call:

PUT /robots/{robot_id}

By sending a request that attempts to update a robot account, and specifying a robot
account id and robot account name that belongs to a different project that the user
doesn’t have access to, it was possible to revoke the robot account permissions.

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
- https://github.com/goharbor/harbor/security/advisories/GHSA-xx9w-464f-7h6f
- https://nvd.nist.gov/vuln/detail/CVE-2022-31667
- https://github.com/goharbor/harbor
