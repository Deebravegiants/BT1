# [H] run-terraform allows for RCE via terraform plan

## Summary
Severity: High
Advisory: GHSA-f9qj-7gh3-mhj4
CVE: CVE-2022-39326
CWE: CWE-94
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-f9qj-7gh3-mhj4
Type: github-advisory

## Affected
- GitHub Actions: `kartverket/github-workflows` — affected >=0 <2.7.5

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_  
All users of the `run-terraform` reusable workflow from the kartverket/github-workflows repo are affected. A malicious actor could potentially send a PR with a malicious payload leading to execution of arbitrary JavaScript code in the context of the workflow.

### Patches
_Has the problem been patched? What versions should users upgrade to?_  
Upgrade to at least 2.7.5 to resolve the issue.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_  
Until you are able to upgrade, make sure to review any PRs from exernal users for malicious payloads before allowing them to trigger a build.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [kartverket/github-workflows](https://github.com/kartverket/github-workflows)

## References
- https://github.com/kartverket/github-workflows/security/advisories/GHSA-f9qj-7gh3-mhj4
- https://nvd.nist.gov/vuln/detail/CVE-2022-39326
- https://github.com/kartverket/github-workflows/pull/19
- https://github.com/kartverket/github-workflows
- https://github.com/kartverket/github-workflows/releases/tag/v2.7.5
