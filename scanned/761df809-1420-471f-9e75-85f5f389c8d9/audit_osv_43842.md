# [M] Rancher: ext.cattle.io/v1 Token store: cross-user token disclosure via label-selector scoping bypass

## Summary
Severity: Medium
Advisory: CVE-2026-75035
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-75035
Type: osv

## Details
A flaw was found in Rancher Manager. When a non-administrative caller supplied a label selector naming a different user, the ext.cattle.io/v1 Token store dropped its internal owner filter instead of returning an empty result. Any authenticated user could therefore list and watch every other user's tokens, disclosing token metadata and the stored salted hash of the bearer token.



This issue affects Rancher: before 2.15.1.

## References
- https://github.com/rancher/rancher/releases/tag/v2.15.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75035.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75035
- https://github.com/rancher/rancher
