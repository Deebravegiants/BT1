# [H] aws-iam-authenticator allow-listed IAM identity may be able to modify their username, escalate privileges before v0.5.9

## Summary
Severity: High
Advisory: GHSA-pp3f-98qg-5g75
CVE: CVE-2022-2385
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-07-13
Source: https://github.com/advisories/GHSA-pp3f-98qg-5g75
Type: github-advisory

## Affected
- Go: `sigs.k8s.io/aws-iam-authenticator` — affected >=0 <0.5.9

## Details
A security issue was discovered in aws-iam-authenticator where an allow-listed IAM identity may be able to modify their username and escalate privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2385
- https://github.com/kubernetes-sigs/aws-iam-authenticator/issues/472
- https://github.com/kubernetes-sigs/aws-iam-authenticator/pull/469
- https://github.com/kubernetes-sigs/aws-iam-authenticator/commit/029d1dcf2ec8d662d9b1c21260bb197404bc8218
- https://github.com/kubernetes-sigs/aws-iam-authenticator
- https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/tag/v0.5.9
- https://groups.google.com/a/kubernetes.io/g/dev/c/EMxHpU-1ZYs
