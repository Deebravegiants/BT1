# [H] CVE-2018-18264

## Summary
Severity: High
Advisory: CVE-2018-18264
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-03
Source: https://osv.dev/vulnerability/CVE-2018-18264
Type: osv

## Details
Kubernetes Dashboard before 1.10.1 allows attackers to bypass authentication and use Dashboard's Service Account for reading secrets within the cluster.

## References
- https://groups.google.com/forum/#%21topic/kubernetes-announce/yBrFf5nmvfI
- http://www.securityfocus.com/bid/106493
- https://github.com/kubernetes/dashboard/releases/tag/v1.10.1
- https://github.com/kubernetes/dashboard/pull/3289
- https://github.com/kubernetes/dashboard/pull/3400
- https://sysdig.com/blog/privilege-escalation-kubernetes-dashboard/
