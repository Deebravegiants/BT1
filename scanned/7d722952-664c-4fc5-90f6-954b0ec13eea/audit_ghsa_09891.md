# [C] Spinnaker: RCE when using gitrepo artifact types due to improper sanitization of user input on branch and paths

## Summary
Severity: Critical
Advisory: GHSA-x3j7-7pgj-h87r
CVE: CVE-2026-32604
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-x3j7-7pgj-h87r
Type: github-advisory

## Affected
- Maven: `io.spinnaker.clouddriver:clouddriver-artifacts-gitrepo` — affected >=0 <2026.0.1

## Details
Spinnaker is an open source, multi-cloud continuous delivery platform. In versions prior to 2026.1.0, 2026.0.1, 2025.4.2, and 2025.3.2, a bad actor can execute arbitrary commands very simply on the clouddriver pods. This can expose credentials, remove files, or inject resources easily. Versions 2026.1.0, 2026.0.1, 2025.4.2, and 2025.3.2 contain a patch. As a workaround, disable the gitrepo artifact types.

## References
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-x3j7-7pgj-h87r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32604
- https://github.com/spinnaker/spinnaker
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2025.3.2
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2025.4.2
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2026.0.1
- https://github.com/spinnaker/spinnaker/releases/tag/spinnaker-release-2026.0.2
- https://zeropath.com/blog/spinnaker-rce-production-compromise
