# [M] Argo Exposure of Sensitive Information 

## Summary
Severity: Medium
Advisory: GHSA-xj7v-c82w-92q2
CVE: CVE-2018-21034
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xj7v-c82w-92q2
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=0 <1.5.0-rc1

## Details
In Argo versions prior to v1.5.0-rc1, it was possible for authenticated Argo users to submit API calls to retrieve secrets and other manifests which were stored within git.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21034
- https://github.com/argoproj/argo-cd/issues/470
- https://github.com/argoproj/argo-cd/pull/3088
- https://github.com/argoproj/argo-cd/commit/916d4aed5775fead4ab75f47c1d352cd0e73b815
- https://github.com/argoproj/argo-cd
- https://github.com/argoproj/argo-cd/blob/a1afe44066fcd0a0ab90a02a23177164bbad42cf/util/diff/diff.go#L399
- https://www.soluble.ai/blog/argo-cves-2020
