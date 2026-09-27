# [H] Rancher Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: GHSA-gc62-j469-9gjm
CVE: CVE-2019-12274
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gc62-j469-9gjm
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0 <2.2.4
- Go: `github.com/rancher/rancher` — affected >=0 <1.6.27

## Details
In Rancher 1 and 2 through 2.2.3, unprivileged users (if allowed to deploy nodes) can gain admin access to the Rancher management plane because node driver options intentionally allow posting certain data to the cloud. The problem is that a user could choose to post a sensitive file such as /root/.kube/config or /var/lib/rancher/management-state/cred/kubeconfig-system.yaml.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12274
- https://forums.rancher.com/t/rancher-release-v2-2-4-addresses-rancher-cve-2019-12274-and-cve-2019-12303/14466
