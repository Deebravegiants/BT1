# [H] CoreDNS ACL Bypass

## Summary
Severity: High
Advisory: GHSA-c9v3-4pv7-87pr
CVE: CVE-2026-26017
CWE: CWE-367
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-c9v3-4pv7-87pr
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.14.2

## Details
A logical vulnerability in CoreDNS allows DNS access controls to be bypassed due to the default execution order of plugins. Security plugins such as acl are evaluated before the rewrite plugin, resulting in a Time-of-Check Time-of-Use (TOCTOU) flaw.


### Impact

In multi-tenant Kubernetes clusters, this flaw undermines DNS-based segmentation strategies.

Example scenario:
1. ACL blocks access to *.admin.svc.cluster.local
2. A rewrite rule maps public-name → admin.svc.cluster.local
3. An unprivileged pod queries public-name
4. ACL allows the request
5. Rewrite exposes the internal admin service IP

This allows unauthorized service discovery and reconnaissance of restricted internal infrastructure.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds

- Reorder the default plugin.cfg so that:
   - rewrite and other normalization plugins run before acl, opa, and firewall
- Ensure all access control checks are applied after name normalization.

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-c9v3-4pv7-87pr
- https://nvd.nist.gov/vuln/detail/CVE-2026-26017
- https://github.com/coredns/coredns
- https://github.com/coredns/coredns/releases/tag/v1.14.2
