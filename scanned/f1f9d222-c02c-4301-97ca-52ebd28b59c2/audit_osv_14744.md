# [H] CVE-2019-11248

## Summary
Severity: High
Advisory: CVE-2019-11248
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-11248
Type: osv

## Details
The debugging endpoint /debug/pprof is exposed over the unauthenticated Kubelet healthz port. The go pprof endpoint is exposed over the Kubelet's healthz port. This debugging endpoint can potentially leak sensitive information such as internal Kubelet memory addresses and configuration, or for limited denial of service. Versions prior to 1.15.0, 1.14.4, 1.13.8, and 1.12.10 are affected. The issue is of medium severity, but not exposed by the default configuration.

## References
- https://groups.google.com/d/msg/kubernetes-security-announce/pKELclHIov8/BEDtRELACQAJ
- https://security.netapp.com/advisory/ntap-20190919-0003/
- https://github.com/kubernetes/kubernetes/issues/81023
