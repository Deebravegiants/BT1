# [H] Long-lived Rancher registration token exposed in plaintext

## Summary
Severity: High
Advisory: CVE-2026-55997
Aliases: GHSA-7r53-jvhg-9jq4
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-55997
Type: osv

## Details
Rancher issues long-lived registration tokens to authenticate nodes and agents joining a downstream cluster. These tokens were stored and exposed in plaintext with no expiration, so a malicious user could obtain one either through the Rancher API, etcd, stored automation, or direct file access on a node, and could use it at any time to register a rogue node into the cluster.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55997.json
- https://github.com/rancher/rancher/security/advisories/GHSA-7r53-jvhg-9jq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55997
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-55997
