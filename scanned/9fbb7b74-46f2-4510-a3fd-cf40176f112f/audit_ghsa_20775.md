# [H] Harbor fails to validate the user permissions when viewing Webhook policies

## Summary
Severity: High
Advisory: GHSA-jf8p-3vjh-pq94
CVE: CVE-2022-31666
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-jf8p-3vjh-pq94
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.0.0 <1.10.13
- Go: `github.com/goharbor/harbor` — affected >=2.0.0 <2.4.3
- Go: `github.com/goharbor/harbor` — affected >=2.5.0 <2.5.2

## Details
### Impact
Harbor fails to validate the user permissions to view Webhook policies including relevant credentials configured in different projects the user doesn’t have access to, resulting in malicious users being able to read Webhook policies of other users/projects. API call is

  GET /projects/{project_name_or_id}/webhook/policies/{webhook_policy_id}

By sending the below request and specifying different Webhook policy ids in the last part of the URL, the malicious user may disclose Webhook policies related to other repositories/projects.: none;">

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
- https://github.com/goharbor/harbor/security/advisories/GHSA-8hwq-5f22-jfr3
- https://github.com/goharbor/harbor/security/advisories/GHSA-jf8p-3vjh-pq94
- https://nvd.nist.gov/vuln/detail/CVE-2022-31666
- https://github.com/goharbor/harbor
