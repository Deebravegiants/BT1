# [M] Unauthenticated users can exploit an enumeration vulnerability in Harbor (CVE-2019-19030)

## Summary
Severity: Medium
Advisory: GHSA-q9x4-q76f-5h5j
CVE: CVE-2019-19030
CWE: CWE-204
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-q9x4-q76f-5h5j
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.7.0 <1.10.3
- Go: `github.com/goharbor/harbor` — affected >=2.0.0 <2.0.1

## Details
# Impact
Sean Wright from Secureworks has discovered an enumeration vulnerability. An attacker can make use of the Harbor API to make unauthenticated calls to the Harbor instance. Based on the HTTP status code in the response, an attacker is then able to work out which resources exist, and which do not. This would likely be accomplished by either providing a wordlist or enumerating through a sequence an
unauthenticated attacker is able to enumerate resources on the system. This provides them with information such as existing projects, repositories, etc.

The vulnerability was immediately fixed by the Harbor team.  

# Issue 
The following API resources where found to be vulnerable to enumeration attacks:
/api/chartrepo/{repo}/prov (POST)
/api/chartrepo/{repo}/charts (GET, POST)
/api/chartrepo/{repo}/charts/{name} (GET, DELETE)
/api/chartrepo/{repo}/charts/{name}/{version} (GET, DELETE)
/api/labels?name={name}&scope=p (GET)
/api/repositories?project_id={id} (GET)
/api/repositories/{repo_name}/ (GET, PUT, DELETE)
/api/repositories/{repo_name}/tags (GET)
/api/repositories/{repo_name}/tags/{tag}/manifest?version={version} (GET)
/api/repositories/{repo_name/{tag}/labels (GET)
/api/projects?project_name={name} (HEAD)
/api/projects/{project_id}/summary (GET)
/api/projects/{project_id}/logs (GET)
/api/projects/{project_id} (GET, PUT, DELETE)
/api/projects/{project_id}/metadatas (GET, POST)
/api/projects/{project_id}/metadatas/{metadata_name} (GET, PUT)

# Known Attack Vectors
Successful exploitation of this issue will lead to bad actors identifying which resources exist in Harbor without requiring authentication for the Harbor API.

# Patches
If your product uses the affected releases of Harbor, update to version 1.10.3 or 2.0.1 to patch this issue immediately.

https://github.com/goharbor/harbor/releases/tag/v1.10.3
https://github.com/goharbor/harbor/releases/tag/v2.0.1

# Workarounds
There is no known workaround

# For more information
If you have any questions or comments about this advisory, contact cncf-harbor-security@lists.cncf.io
View our security policy at https://github.com/goharbor/harbor/security/policy

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-q9x4-q76f-5h5j
- https://nvd.nist.gov/vuln/detail/CVE-2019-19030
- https://github.com/goharbor/harbor
