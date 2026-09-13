# [H] Git credentials are exposed in Atlantis logs

## Summary
Severity: High
Advisory: GHSA-gppm-hq3p-h4rp
CVE: CVE-2024-52009
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2024-11-08
Source: https://github.com/advisories/GHSA-gppm-hq3p-h4rp
Type: github-advisory

## Affected
- Go: `github.com/runatlantis/atlantis` — affected >=0 <0.30.0

## Details
### Summary
_Short summary of the problem. Make the impact and severity as clear as possible. For example: An unsafe deserialization vulnerability allows any unauthenticated user to execute arbitrary code on the server._

Atlantis logs contains GitHub credentials (tokens `ghs_...`) when they are rotated. This enables an attacker able to read these logs to impersonate Atlantis application and to perform actions on GitHub.

When Atlantis is used to administer a GitHub organization, this enables getting administration privileges on the organization.

This was reported in https://github.com/runatlantis/atlantis/issues/4060 and fixed in https://github.com/runatlantis/atlantis/pull/4667 . The fix was included in [Atlantis v0.30.0](https://github.com/runatlantis/atlantis/releases/tag/v0.30.0).

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

While auditing the Kubernetes/Argo CD/Atlantis deployment of some company, the following set-up was encountered:

- Most employees have read-only access to Argo CD, enabling them to see the health of deployed applications.
- Atlantis was deployed as an Argo CD application.
- Atlantis was used to manage the configuration of a GitHub organization (such as team members), using [Terraform's GitHub integration](https://registry.terraform.io/providers/integrations/github/latest).

Atlantis logs on Argo CD contained lines such as:

```json
{"level":"debug","ts":"2024-11-07T17:58:30.636Z","caller":"vcs/gh_app_creds_rotator.go:58","msg":"Refreshing git tokens for Github App","json":{}}
{"level":"debug","ts":"2024-11-07T17:58:30.637Z","caller":"vcs/gh_app_creds_rotator.go:64","msg":"token ghs_[REDACTED]","json":{}}
{"level":"debug","ts":"2024-11-07T17:58:30.637Z","caller":"vcs/git_cred_writer.go:36","msg":"git credentials file has expected contents, not modifying","json":{}}
```

This enabled employees with read-only access to Argo CD to get administration privileges on the GitHub organization, compromising all repositories. As some repositories were used for Infrastructure-as-Code deployment (with Atlantis), this enabled the security auditors to get cluster admin privileges on most Kubernetes clusters.

While the set-up "most employees have read-only access to Argo CD" can be seen as dangerous, this should not incur such security risk (cf. https://argo-cd.readthedocs.io/en/stable/operator-manual/security/). The main issue here was that the logs contained privileged GitHub tokens as they were obtained by Atlantis.

This issue was already reported  (https://github.com/runatlantis/atlantis/issues/4060) and fixed (https://github.com/runatlantis/atlantis/pull/4667) but no security advisory was published on https://github.com/runatlantis/atlantis/security and no CVE was assigned (https://app.opencve.io/cve/?&vendor=runatlantis&product=atlantis only lists [CVE-2022-24912](https://nvd.nist.gov/vuln/detail/CVE-2022-24912), which is unrelated).

Could you please publish a security advisory?

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

cf. https://github.com/runatlantis/atlantis/issues/4060 for more details.

### Impact
_What kind of vulnerability is it? Who is impacted?_

- This leaks sensitive GitHub tokens in the log files (CWE-532: Insertion of Sensitive Information into Log File).
- This could enable anyone with log read access to compromiseGitHub organizations managed by Atlantis.
- This impact at least users using Atlantis with Github application and integration.

## References
- https://github.com/runatlantis/atlantis/security/advisories/GHSA-gppm-hq3p-h4rp
- https://nvd.nist.gov/vuln/detail/CVE-2024-52009
- https://github.com/runatlantis/atlantis/issues/4060
- https://github.com/runatlantis/atlantis/pull/4667
- https://github.com/runatlantis/atlantis/commit/0def7d3fb74aabb75570554692b053950cde02e1
- https://argo-cd.readthedocs.io/en/stable/operator-manual/security
- https://github.com/runatlantis/atlantis
- https://github.com/runatlantis/atlantis/releases/tag/v0.30.0
- https://pkg.go.dev/vuln/GO-2024-3265
