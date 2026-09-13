# [M] Jenkins Gogs Plugin vulnerable to unsafe default behavior and information disclosure

## Summary
Severity: Medium
Advisory: GHSA-qxwc-wchr-5h29
CVE: CVE-2023-40348
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-qxwc-wchr-5h29
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gogs-webhook` — affected >=0

## Details
Jenkins Gogs Plugin provides a webhook endpoint at `/gogs-webhook` that can be used to trigger builds of jobs. In Gogs Plugin 1.0.15 and earlier, an option to specify a Gogs secret for this webhook is provided, but not enabled by default.

This allows unauthenticated attackers to trigger builds of jobs corresponding to the attacker-specified job name.

Additionally, the output of the webhook endpoint includes whether a job corresponding to the attacker-specified job name exists, even if the attacker has no permission to access it.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40348
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-2894
- http://www.openwall.com/lists/oss-security/2023/08/16/3
