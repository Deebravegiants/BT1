# [M] Moby (Docker Engine) Insufficiently restricted permissions on data directory

## Summary
Severity: Medium
Advisory: GHSA-3fwx-pjgw-3558
CVE: CVE-2021-41091
CWE: CWE-281, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-3fwx-pjgw-3558
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <20.10.9
- Go: `github.com/docker/docker` — affected >=0 <20.10.9

## Details
## Impact

A bug was found in Moby (Docker Engine) where the data directory (typically `/var/lib/docker`) contained subdirectories with insufficiently restricted permissions, allowing otherwise unprivileged Linux users to traverse directory contents and execute programs.  When containers included executable programs with extended permission bits (such as `setuid`), unprivileged Linux users could discover and execute those programs.  When the UID of an unprivileged Linux user on the host collided with the file owner or group inside a container, the unprivileged Linux user on the host could discover, read, and modify those files.

## Patches

This bug has been fixed in Moby (Docker Engine) 20.10.9.  Users should update to this version as soon as possible.  Running containers should be stopped and restarted for the permissions to be fixed.

## Workarounds

Limit access to the host to trusted users.  Limit access to host volumes to trusted containers.

## Credits

The Moby project would like to thank Joan Bruguera for responsibly disclosing this issue in accordance with the [Moby security policy](https://github.com/moby/moby/blob/master/SECURITY.md).

## For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/moby/moby/issues/new)
* Email us at security@docker.com if you think you’ve found a security bug

## References
- https://github.com/moby/moby/security/advisories/GHSA-3fwx-pjgw-3558
- https://nvd.nist.gov/vuln/detail/CVE-2021-41091
- https://github.com/moby/moby/commit/f0ab919f518c47240ea0e72d0999576bb8008e64
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://github.com/moby/moby
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B5Q6G6I4W5COQE25QMC7FJY3I3PAYFBB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZNFADTCHHYWVM6W4NJ6CB4FNFM2VMBIB
