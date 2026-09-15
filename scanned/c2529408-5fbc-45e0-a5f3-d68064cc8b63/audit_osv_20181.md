# [C] CVE-2021-31921

## Summary
Severity: Critical
Advisory: CVE-2021-31921
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-31921
Type: osv

## Details
Istio before 1.8.6 and 1.9.x before 1.9.5 contains a remotely exploitable vulnerability where an external client can access unexpected services in the cluster, bypassing authorization checks, when a gateway is configured with AUTO_PASSTHROUGH routing configuration.

## References
- https://istio.io/latest/news/security/istio-security-2021-006/
