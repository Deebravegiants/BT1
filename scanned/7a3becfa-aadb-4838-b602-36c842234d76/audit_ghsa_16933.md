# [H] Rancher Privilege escalation vulnerability via malicious "Connection" header

## Summary
Severity: High
Advisory: GHSA-pvxj-25m6-7vqr
CVE: CVE-2021-31999
CWE: CWE-807
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-pvxj-25m6-7vqr
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0 <2.4.16
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.9

## Details
A vulnerability was discovered in Rancher 2.0.0 through the aforementioned patched versions, where a malicious Rancher user could craft an API request directed at the proxy for the Kubernetes API of a managed cluster to gain access to information they do not have access to. This is done by passing the "Impersonate-User" or "Impersonate-Group" header in the Connection header, which is then correctly removed by the proxy. At this point, instead of impersonating the user and their permissions, the request will act as if it was from the Rancher management server and incorrectly return the information. The vulnerability is limited to valid Rancher users with some level of permissions on the cluster. There is not a direct mitigation besides upgrading to the patched Rancher versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31999
- https://bugzilla.suse.com/show_bug.cgi?id=1187084
- https://github.com/rancher/rancher
- https://pkg.go.dev/vuln/GO-2024-2778
