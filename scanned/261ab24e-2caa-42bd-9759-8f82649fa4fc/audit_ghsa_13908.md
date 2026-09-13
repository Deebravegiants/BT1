# [M] Openshift Enterprise source-to-image vulnerable to Arbitrary File Write via Archive Extraction (Zip Slip)

## Summary
Severity: Medium
Advisory: GHSA-w55j-f7vx-6q37
CVE: CVE-2018-1103
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-w55j-f7vx-6q37
Type: github-advisory

## Affected
- Go: `github.com/openshift/source-to-image` — affected >=0 <1.1.10-0.20180427153919-f5cbcbc5cc6f

## Details
Openshift Enterprise source-to-image before version 1.1.10 is vulnerable to an improper validation of user input. An attacker who could trick a user into using the command to copy files locally, from a pod, could override files outside of the target directory of the command.

### Specific Go Packages Affected
github.com/openshift/source-to-image/pkg/tar

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1103
- https://github.com/openshift/source-to-image/pull/870
- https://github.com/openshift/source-to-image/commit/f5cbcbc5cc6f8cc2f479a7302443bea407a700cb
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1103
- https://github.com/openshift/source-to-image
- https://github.com/snyk/zip-slip-vulnerability
- https://hansmi.ch/articles/2018-04-openshift-s2i-security
- https://pkg.go.dev/vuln/GO-2020-0026
- https://snyk.io/research/zip-slip-vulnerability
