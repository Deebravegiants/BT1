# [M] Harbor fails to validate the user permissions when reading job execution logs through the P2P preheat execution logs

## Summary
Severity: Medium
Advisory: GHSA-q76q-q8hw-hmpw
CVE: CVE-2022-31671
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-09
Source: https://github.com/advisories/GHSA-q76q-q8hw-hmpw
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.0.0 <1.10.13
- Go: `github.com/goharbor/harbor` — affected >=2.0.0 <2.4.3
- Go: `github.com/goharbor/harbor` — affected >=2.5.0 <2.5.2

## Details
### Impact
Harbor fails to validate the user permissions when reading job execution logs through the P2P preheat execution logs - API call

  GET /projects/{project_name}/preheat/policies/{preheat_policy_name}/executions/{execution_id}/tasks/{task_id}/logs

By sending a request that attempts to read P2P preheat execution logs and specifying different job ids, malicious authenticatedusers could read all the job logs stored in the Harbor database.

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
- https://github.com/goharbor/harbor/security/advisories/GHSA-3wpx-625q-22j7
- https://github.com/goharbor/harbor/security/advisories/GHSA-q76q-q8hw-hmpw
- https://nvd.nist.gov/vuln/detail/CVE-2022-31671
- https://github.com/goharbor/harbor
