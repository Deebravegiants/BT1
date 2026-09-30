# [H] CVE-2021-34824

## Summary
Severity: High
Advisory: CVE-2021-34824
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-29
Source: https://osv.dev/vulnerability/CVE-2021-34824
Type: osv

## Details
Istio (1.8.x, 1.9.0-1.9.5 and 1.10.0-1.10.1) contains a remotely exploitable vulnerability where credentials specified in the Gateway and DestinationRule credentialName field can be accessed from different namespaces.

## References
- https://github.com/istio/istio/releases
- https://istio.io/latest/news/security/istio-security-2021-007
