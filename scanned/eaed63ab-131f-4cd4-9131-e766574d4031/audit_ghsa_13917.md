# [M] Kubernetes client-go vulnerable to Sensitive Information Leak via Log File

## Summary
Severity: Medium
Advisory: GHSA-8cfg-vx93-jvxw
CVE: CVE-2020-8565
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-8cfg-vx93-jvxw
Type: github-advisory

## Affected
- Go: `k8s.io/client-go` — affected >=0.19.0 <0.19.6
- Go: `k8s.io/client-go` — affected >=0.20.0-alpha.0 <0.20.0-alpha.2
- Go: `k8s.io/client-go` — affected >=0.18.0 <0.18.14
- Go: `k8s.io/client-go` — affected >=0 <0.17.16
- Go: `k8s.io/kubernetes` — affected >=0 <1.20.0-alpha.2

## Details
In Kubernetes, if the logging level is set to at least 9, authorization and bearer tokens will be written to log files. This can occur both in API server logs and client tool output like kubectl. This affects <= v1.19.5, <= v1.18.13, <= v1.17.15, < v1.20.0-alpha2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8565
- https://github.com/kubernetes/kubernetes/issues/95623
- https://github.com/kubernetes/kubernetes/pull/95316
- https://github.com/kubernetes/client-go/commit/19875a3d5a2e0d4f51c976a9e0662de3c2c011e3
- https://github.com/kubernetes/client-go/commit/1b8383fc150c9b816b0072032cca75754c2734d0
- https://github.com/kubernetes/client-go/commit/44e1a07f2d513e375c4b6ee6e890040b47befe86
- https://github.com/kubernetes/client-go/commit/e8f871a2e5fadf90fc114565abc0963967f1a373
- https://github.com/kubernetes/kubernetes/commit/e99df0e5a75eb6e86123b56d53e9b7ca0fd00419
- https://github.com/kubernetes/client-go
- https://groups.google.com/g/kubernetes-security-discuss/c/vm-HcrFUOCs/m/36utxAM5CwAJ
- https://pkg.go.dev/vuln/GO-2021-0064
