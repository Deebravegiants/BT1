# [M] Pinniped Supervisor Insufficient Session Expiration vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rp4v-hhm6-rcv9
CVE: CVE-2022-31677
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-01
Source: https://github.com/advisories/GHSA-rp4v-hhm6-rcv9
Type: github-advisory

## Affected
- Go: `go.pinniped.dev` — affected >=0.3.0 <0.19.0

## Details
### Impact

A user authenticating to Kubernetes clusters via the Pinniped Supervisor could potentially use their access token to continue their session beyond what proper use of their refresh token might allow.

Access tokens issued by the Pinniped Supervisor have an intended expiration lifetime of approximately two minutes. The Pinniped CLI will automatically use the refresh token, which has a lifetime of approximately nine hours, to request a new access token after the access token's advertised expiration time elapses. Starting in Pinniped version 0.13.0, the Supervisor performs checks during each refresh request against the configured external identity provider to determine if the user should be allowed to continue their session. Thus, the short lifetime of the access token is intended to force users to be subjected to those checks often. For example, if a user's account in the external identity provider became locked, the next refresh would fail, and the user should lose access to the Kubernetes clusters fairly quickly. As another example, if a user's group membership changed in the external identity provider, the new group memberships would be reflected in their sessions with Kubernetes clusters within a fairly short window of time.

Access tokens are cached in a local file by the Pinniped CLI (the kubectl plugin) and are sent back to the Supervisor (via HTTPS) to receive cluster-scoped credentials. Due to a bug in this token exchange, the expiration time of the submitted access token was not checked correctly, causing expired access tokens to continue to be accepted by this endpoint until the user's backend session data is deleted, approximately nine hours after their session started. This bug could allow a legitimate user to avoid the checks performed during refresh by maliciously skipping the refresh step.

Note that the Pinniped CLI performs the refresh operation often, so the refresh checks are still performed often under normal usage of the CLI, despite this bug.

Practical impact to versions before v0.13.0 is minimal, since those versions did not perform checks against the external identity provider during refreshes. In these versions, the user can perform refreshes to get a new access tokens without restriction for approximately nine hours, so the duration of their access is effectively unchanged by this bug.

### Patches

The impacted token exchange feature was first introduced in v0.3.0. Versions v0.3.0 to v0.18.0 are effected by this bug.

This vulnerability was found by the maintainers of Pinniped and fixed immediately. The fix was introduced in release v0.19.0.

### Workarounds

There are no known workarounds. Upgrading the Supervisor is recommended, especially for users of v0.13.0 or newer.

### References

The issue was fixed by PR [#1264](https://github.com/vmware-tanzu/pinniped/pull/1264).

### For more information

If you have any questions or comments about this advisory, please reach out to the maintainers using one of the methods described in this repo's [README.md](https://github.com/vmware-tanzu/pinniped/blob/main/README.md#discussion).

## References
- https://github.com/vmware-tanzu/pinniped/security/advisories/GHSA-rp4v-hhm6-rcv9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31677
- https://github.com/vmware-tanzu/pinniped/pull/1264
- https://github.com/vmware-tanzu/pinniped
- https://github.com/vmware-tanzu/pinniped/releases/tag/v0.19.0
