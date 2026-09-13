# [H] Kubernetes did not effectively clear service account credentials

## Summary
Severity: High
Advisory: GHSA-gc2p-g4fg-29vh
CVE: CVE-2019-11243
CWE: CWE-212, CWE-271
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gc2p-g4fg-29vh
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.12.0 <1.12.5
- Go: `k8s.io/kubernetes` — affected >=1.13.0 <1.13.1

## Details
In Kubernetes v1.12.0-v1.12.4 and v1.13.0, the rest.AnonymousClientConfig() method returns a copy of the provided config, with credentials removed (bearer token, username/password, and client certificate/key data). In the affected versions, rest.AnonymousClientConfig() did not effectively clear service account credentials loaded using rest.InClusterConfig()

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11243
- https://github.com/kubernetes/kubernetes/issues/76797
- https://github.com/kubernetes/kubernetes
- https://security.netapp.com/advisory/ntap-20190509-0002
