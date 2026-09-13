# [C] Privilege Escalation in Kubernetes

## Summary
Severity: Critical
Advisory: GHSA-579h-mv94-g4gp
CVE: CVE-2018-1002105
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-579h-mv94-g4gp
Type: github-advisory

## Affected
- Go: `github.com/kubernetes/kubernetes` — affected >=0 <1.10.11
- Go: `github.com/kubernetes/kubernetes` — affected >=1.11.0 <1.11.5
- Go: `github.com/kubernetes/kubernetes` — affected >=1.12.0 <1.12.3

## Details
In all Kubernetes versions prior to v1.10.11, v1.11.5, and v1.12.3, incorrect handling of error responses to proxied upgrade requests in the kube-apiserver allowed specially crafted requests to establish a connection through the Kubernetes API server to backend servers, then send arbitrary requests over the same connection directly to the backend, authenticated with the Kubernetes API server's TLS credentials used to establish the backend connection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002105
- https://github.com/kubernetes/kubernetes/issues/71411
- https://github.com/kubernetes/kubernetes/commit/2257c1ecbe3c0cf71dd50b82752ae189c94ec905
- https://www.securityfocus.com/bid/106068
- https://www.openwall.com/lists/oss-security/2019/07/06/4
- https://www.openwall.com/lists/oss-security/2019/07/06/3
- https://www.openwall.com/lists/oss-security/2019/06/28/2
- https://www.exploit-db.com/exploits/46053
- https://www.exploit-db.com/exploits/46052
- https://www.coalfire.com/The-Coalfire-Blog/December-2018/Kubernetes-Vulnerability-What-You-Can-Should-Do
- https://security.netapp.com/advisory/ntap-20190416-0001
- https://lists.opensuse.org/opensuse-security-announce/2020-04/msg00041.html
- https://groups.google.com/forum/#!topic/kubernetes-announce/GVllWCg6L88
- https://github.com/evict/poc_CVE-2018-1002105
- https://access.redhat.com/errata/RHSA-2018:3754
- https://access.redhat.com/errata/RHSA-2018:3752
- https://access.redhat.com/errata/RHSA-2018:3742
- https://access.redhat.com/errata/RHSA-2018:3624
- https://access.redhat.com/errata/RHSA-2018:3598
- https://access.redhat.com/errata/RHSA-2018:3551
