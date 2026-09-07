# [H] Rancher allows an unauthenticated stack overflow in /v3-public/authproviders API

## Summary
Severity: High
Advisory: GHSA-xr9q-h9c7-xw8q
CVE: CVE-2025-23388
CWE: CWE-121
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-02-27
Source: https://github.com/advisories/GHSA-xr9q-h9c7-xw8q
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.8.0 <2.8.13
- Go: `github.com/rancher/rancher` — affected >=2.9.0 <2.9.7
- Go: `github.com/rancher/rancher` — affected >=2.10.0 <2.10.3

## Details
### Impact
An unauthenticated stack overflow crash, leading to a denial of service (DoS), was identified in Rancher’s `/v3-public/authproviders` public API endpoint. A malicious user could submit data to the API which would cause the Rancher server to crash, but no malicious or incorrect data would actually be written in the API. The downstream clusters, i.e., the clusters managed by Rancher, are not affected by this issue.

This vulnerability affects those using external authentication providers as well as Rancher’s local authentication.

### Patches
The patch includes the removal of unnecessary HTTP methods of the specific API.

Patched versions include releases `v2.8.13`, `v2.9.7` and `v2.10.3`.

### Workarounds
There are no workarounds for this issue. Users are recommended to upgrade, as soon as possible, to a version of Rancher Manager that contains the fix.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-xr9q-h9c7-xw8q
- https://github.com/rancher/rancher/pull/48608
- https://github.com/rancher/rancher/pull/48954
- https://github.com/rancher/rancher/pull/48957
- https://github.com/rancher/rancher/pull/48958
- https://github.com/rancher/rancher/commit/5c7aded42509ae526383bb296138e8ea0dff9d13
- https://github.com/rancher/rancher/commit/92d55b799ac172734106569b61ca87bbd5affcb2
- https://github.com/rancher/rancher/commit/a263bf3466717ee4bab802d499a5a167d274813d
- https://github.com/rancher/rancher/commit/de3ffa88cc75ae3da122bd36a4489663b5157ee3
- https://github.com/rancher/rancher
- https://github.com/rancher/rancher/releases/tag/v2.10.3
- https://github.com/rancher/rancher/releases/tag/v2.8.13
- https://github.com/rancher/rancher/releases/tag/v2.9.7
