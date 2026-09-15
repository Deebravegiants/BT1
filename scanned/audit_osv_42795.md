# [M] Rancher: Identity-field mutation in /v3/users allows account hijack via principal rebind

## Summary
Severity: Medium
Advisory: CVE-2026-71403
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-71403
Type: osv

## Details
A flaw was found in Rancher Manager. The /v3/users update path did not enforce immutability of a User resource's `username` and `principalIds` fields. A user holding the `update` verb on `users.management.cattle.io` could inject a foreign identity provider principal into any account, so that the next login by the owner of that principal was bound to the victim's account and inherited its role bindings.


This issue affects Rancher: before 2.15.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71403.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71403
- https://github.com/rancher/rancher/pull/56616
- https://github.com/rancher/rancher
