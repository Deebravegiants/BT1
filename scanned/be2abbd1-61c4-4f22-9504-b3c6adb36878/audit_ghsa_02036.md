# [H] Access control flaw in Kiali

## Summary
Severity: High
Advisory: GHSA-mv55-23xp-3wp8
CVE: CVE-2021-3495
CWE: CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-mv55-23xp-3wp8
Type: github-advisory

## Affected
- Go: `github.com/kiali/kiali` — affected >=0 <1.33.0

## Details
An incorrect access control flaw was found in the kiali-operator in versions before 1.33.0. This flaw allows an attacker with a basic level of access to the cluster (to deploy a kiali operand) to use this vulnerability and deploy a given image to anywhere in the cluster, potentially gaining access to privileged service account tokens. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3495
- https://github.com/kiali/kiali-operator/pull/278
- https://bugzilla.redhat.com/show_bug.cgi?id=1947361
- https://kiali.io/news/security-bulletins/kiali-security-003
