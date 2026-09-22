# [M] CoreWCF: Unix Domain Socket PosixIdentity transport accepts connections that skip the security upgrade

## Summary
Severity: Medium
Advisory: GHSA-wjpq-6766-7f5j
CVE: CVE-2026-54776
CWE: CWE-306
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-wjpq-6766-7f5j
Type: github-advisory

## Affected
- NuGet: `CoreWCF.UnixDomainSocket` — affected >=0 <1.8.1
- NuGet: `CoreWCF.UnixDomainSocket` — affected >=1.9.0 <1.9.1

## Details
### Impact
A CoreWCF service hosted on Unix Domain Sockets with the PosixIdentity client credential type (UnixDomainSocketBinding with Security.Mode = TransportCredentialOnly and Security.Transport.ClientCredentialType = PosixIdentity) does not require the client to perform the application/unixposix stream upgrade before dispatching messages.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
Restrict filesystem access to the UDS socket file using owner/group/mode (e.g. chmod 0660 plus a dedicated group) so that only the POSIX users who are already authorized to invoke the service can connect at all. This makes the missing-upgrade behaviour equivalent to the operating system’s filesystem permissions instead of relying on framing-layer identity checks.
Avoid relying on ServiceSecurityContext.PrimaryIdentity for authorization decisions, or back it up with an authentication-required authorization policy that rejects anonymous principals.

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-wjpq-6766-7f5j
- https://github.com/CoreWCF/CoreWCF
