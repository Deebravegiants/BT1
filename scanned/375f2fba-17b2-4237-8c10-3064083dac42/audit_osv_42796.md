# [H] Rancher: Ownership-less ClusterRole overwrite via attacker-controlled cr-name annotation on GlobalRole

## Summary
Severity: High
Advisory: CVE-2026-71404
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-71404
Type: osv

## Details
A flaw was found in Rancher Manager. The GlobalRole controller derived the target ClusterRole name from the user-settable `authz.management.cattle.io/cr-name` annotation and overwrote that object's rules without verifying ownership. A user with delegated GlobalRole create or update permission could point the annotation at any existing ClusterRole, such as `cluster-admin`, and revoke the permissions of every principal bound to it. The change persists after the malicious GlobalRole is deleted.


This issue affects Rancher: before 2.15.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71404.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71404
- https://github.com/rancher/rancher/pull/56593
- https://github.com/rancher/rancher/pull/56642
- https://github.com/rancher/rancher
