# [M] CVE-2024-5138: snapd snapctl auth bypass

## Summary
Severity: Medium
Advisory: GHSA-p9v8-q5m4-pf46
CVE: CVE-2024-5138
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-p9v8-q5m4-pf46
Type: github-advisory

## Affected
- Go: `github.com/snapcore/snapd` — affected >=2.51.6 <2.63.1
- Go: `github.com/snapcore/snapd` — affected >=0 <0.0.0-20240524114846-68ee9c6aa916

## Details
### Impact

A snap with prior permissions to create a mount entry on the host, such as firefox, normally uses the permission from one of the per-snap hook programs. A unprivileged users cannot normally trigger that behaviour by using `snap run --shell firefox` followed by `snapctl mount`, since snapd validates the requesting user identity (root or non-root). The issue allows unprivileged users to bypass that check by crafting a malicious command line vector which confuses snapd into thinking the help message is requested.

Unprivileged user on a default installation of Ubuntu, where firefox is as provided as a snap, may cause a denial-of-service attack by repeatedly mounting hunspell database over and over and eventually exhausting system memory.

Other attacks, reliant on the same underying mechanism (mount), are possible. In all cases the snap must be installed and grated permission to perform this action (by connecting an appropriate snap interface), which requires administrative privileges. As such we are focusing on the case of default installation where an unprivileged user may exploit this behavior.

### Patches

Patch: https://github.com/canonical/snapd/commit/68ee9c6aa916ab87dbfd9a26030690f2cabf1e14
Release: Available from Snapd 2.64

### Workarounds

Users may disconnect any instances of the mount-control interface to prevent snapd from creating such mount points. For example, the firefox snap has the `host-hunspell` plug, which is of type `mount-control`. The interface can be disconnected with:

```sh
sudo snap disconnect firefox:host-hunspell
```

### References

The original bug report was made on Launchpad: https://bugs.launchpad.net/snapd/+bug/2065077
CVE.org: https://www.cve.org/CVERecord?id=CVE-2024-5138
Canonical: https://ubuntu.com/security/CVE-2024-5138

## References
- https://github.com/canonical/snapd/security/advisories/GHSA-p9v8-q5m4-pf46
- https://github.com/canonical/snapd/commit/68ee9c6aa916ab87dbfd9a26030690f2cabf1e14
- https://bugs.launchpad.net/snapd/+bug/2065077
- https://github.com/canonical/snapd
- https://ubuntu.com/security/CVE-2024-5138
- https://www.cve.org/CVERecord?id=CVE-2024-5138
