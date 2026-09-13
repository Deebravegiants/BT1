# [M] Symlink Attack in kubectl cp

## Summary
Severity: Medium
Advisory: GHSA-34jx-wx69-9x8v
CVE: CVE-2019-1002101
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-34jx-wx69-9x8v
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.11.9
- Go: `k8s.io/kubernetes` — affected >=1.12.0 <1.12.7
- Go: `k8s.io/kubernetes` — affected >=1.13.0 <1.13.5

## Details
The kubectl cp command allows copying files between containers and the user machine. To copy files from a container, Kubernetes creates a tar inside the container, copies it over the network, and kubectl unpacks it on the user’s machine. If the tar binary in the container is malicious, it could run any code and output unexpected, malicious results. An attacker could use this to write files to any path on the user’s machine when kubectl cp is called, limited only by the system permissions of the local user. The untar function can both create and follow symbolic links. The issue is resolved in kubectl v1.11.9, v1.12.7, v1.13.5, and v1.14.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1002101
- https://github.com/kubernetes/kubernetes/pull/75037
- https://github.com/kubernetes/kubernetes/commit/47063891dd782835170f500a83f37cc98c3c1013
- https://access.redhat.com/errata/RHBA-2019:0619
- https://access.redhat.com/errata/RHBA-2019:0620
- https://access.redhat.com/errata/RHBA-2019:0636
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BPV2RE5RMOGUVP5WJMXKQJZUBBLAFZPZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QZB7E3DOZ5WDG46XAIU6K32CXHXPXB2F
- https://www.twistlock.com/labs-blog/disclosing-directory-traversal-vulnerability-kubernetes-copy-cve-2019-1002101
- http://www.openwall.com/lists/oss-security/2019/06/21/1
- http://www.openwall.com/lists/oss-security/2019/08/05/5
- http://www.securityfocus.com/bid/107652
