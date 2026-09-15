# [H] Malicious HTML+XHR Artifact Privilege Escalation in Argo Workflows

## Summary
Severity: High
Advisory: GHSA-cmv8-6362-r5w9
CVE: CVE-2022-29164
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-23
Source: https://github.com/advisories/GHSA-cmv8-6362-r5w9
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=2.6.0 <3.2.11
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.3.0 <3.3.5

## Details
Argo Workflows is an open source container-native workflow engine for orchestrating parallel jobs on Kubernetes.

* The attacker creates a workflow that produces a HTML artifact that contains a HTML file that contains a script which uses XHR calls to interact with the Argo Server API.
* The attacker emails the deep-link to the artifact to their victim. The victim opens the link, the script starts running.

As the script has access to the Argo Server API (as the victim), so may do the following (if the victim may):

* Read information about the victim’s workflows.
* Create or delete workflows.

Notes:

* The attacker must be an insider: they must have access to the same cluster as the victim and must already be able to run their own workflows. 
* The attacker must have an understanding of the victim’s system. They won’t be able to repeatedly probe due to the social engineering  aspect.
* The attacker is likely leave an audit trail.

We have seen no evidence of this in the wild. While the impact is high, it is very hard to exploit. 

We urge all users to upgrade to the fixed versions. Disabling the Argo Server is the only known workaround. Note version 2.12 has been out of support for sometime. No fix is currently planned.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-cmv8-6362-r5w9
- https://nvd.nist.gov/vuln/detail/CVE-2022-29164
- https://github.com/argoproj/argo-workflows/pull/8585
- https://github.com/argoproj/argo-workflows/commit/87470e1c2bf703a9110e97bb755614ce8757fdcc
- github.com/argoproj/argo-workflows
