# [M] Unauthenticated namespace creation and RBAC injection via rancher-webhook FleetWorkspace mutating webhook

## Summary
Severity: Medium
Advisory: CVE-2026-44949
Aliases: GHSA-h83p-cq95-vph4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-44949
Type: osv

## Details
A Rancher FleetWorkspace admission path allowed side effects to occur in
 the Rancher webhook handler for versions 0.7.0 up to 0.7.10, 0.8.0 up to 0.8.7, 0.9.0 up to 0.9.6 and 0.10.0 up to 0.10.7. An unauthenticated attacker with network access to
 the in-cluster rancher-webhook service
 could submit a crafted admission payload and cause workspace-related 
Kubernetes objects to be created with attacker-chosen identity data.

## References
- https://github.com/rancher/webhook/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44949.json
- https://github.com/rancher/webhook/security/advisories/GHSA-h83p-cq95-vph4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44949
