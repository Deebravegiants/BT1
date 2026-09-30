# [M] Access Control Bypass

## Summary
Severity: Medium
Advisory: GHSA-9qq2-xhmc-h9qr
CVE: CVE-2018-20321
CWE: CWE-288, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-9qq2-xhmc-h9qr
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0 <2.1.6

## Details
An issue was discovered in Rancher 2 through 2.1.5. Any project member with access to the default namespace can mount the netes-default service account in a pod, and then use that pod to execute administrative privileged commands against the k8s cluster. This could be mitigated by isolating the default namespace in a separate project, where only cluster admins can be given permissions to access. As of 2018-12-20, this bug affected ALL clusters created or imported by Rancher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20321
- https://github.com/rancher/rancher/commit/6ea187fcc2309d5a7a14ed47de5688bf6573f448
- https://forums.rancher.com/c/announcements
- https://github.com/rancher/rancher
- https://github.com/rancher/rancher/releases/tag/v2.1.6
- https://rancher.com/blog/2019/2019-01-29-explaining-security-vulnerabilities-addressed-in-rancher-v2-1-6-and-v2-0-11
