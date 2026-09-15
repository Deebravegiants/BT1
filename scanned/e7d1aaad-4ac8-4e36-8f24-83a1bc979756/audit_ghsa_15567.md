# [M] runc can be confused to create empty files/directories on the host

## Summary
Severity: Medium
Advisory: GHSA-jfvp-7x6p-h2pv
CVE: CVE-2024-45310
CWE: CWE-363, CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-jfvp-7x6p-h2pv
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=0 <1.1.14
- Go: `github.com/opencontainers/runc` — affected >=1.2.0-rc.1 <1.2.0-rc.3

## Details
### Impact
runc 1.1.13 and earlier as well as 1.2.0-rc2 and earlier can be tricked into
creating empty files or directories in arbitrary locations in the host
filesystem by sharing a volume between two containers and exploiting a race
with os.MkdirAll. While this can be used to create empty files, existing
files **will not** be truncated.

An attacker must have the ability to start containers using some kind of custom
volume configuration. Containers using user namespaces are still affected, but
the scope of places an attacker can create inodes can be significantly reduced.
Sufficiently strict LSM policies (SELinux/Apparmor) can also in principle block
this attack -- we suspect the industry standard SELinux policy may restrict
this attack's scope but the exact scope of protection hasn't been analysed.

This is exploitable using runc directly as well as through Docker and
Kubernetes.

The CVSS score for this vulnerability is
CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (Low severity, 3.6).

### Workarounds
Using user namespaces restricts this attack fairly significantly such that the
attacker can only create inodes in directories that the remapped root
user/group has write access to. Unless the root user is remapped to an actual
user on the host (such as with rootless containers that don't use
/etc/sub[ug]id), this in practice means that an attacker would only be able to
create inodes in world-writable directories.

A strict enough SELinux or AppArmor policy could in principle also restrict the
scope if a specific label is applied to the runc runtime, though we haven't
thoroughly tested to what extent the standard existing policies block this
attack nor what exact policies are needed to sufficiently restrict this attack.

### Patches
Fixed in runc v1.1.14 and v1.2.0-rc3.

* `main` patches:
  * https://github.com/opencontainers/runc/pull/4359
  *  https://github.com/opencontainers/runc/commit/63c2908164f3a1daea455bf5bcd8d363d70328c7
* `release-1.1` patches:
  * https://github.com/opencontainers/runc/commit/8781993968fd964ac723ff5f360b6f259e809a3e
  * https://github.com/opencontainers/runc/commit/f0b652ea61ff6750a8fcc69865d45a7abf37accf

### Credits
Thanks to Rodrigo Campos Catelin (@rata) and Alban Crequy (@alban) from
Microsoft for discovering and reporting this vulnerability.

## References
- https://github.com/opencontainers/runc/security/advisories/GHSA-jfvp-7x6p-h2pv
- https://nvd.nist.gov/vuln/detail/CVE-2024-45310
- https://github.com/opencontainers/runc/pull/4359
- https://github.com/opencontainers/runc/commit/63c2908164f3a1daea455bf5bcd8d363d70328c7
- https://github.com/opencontainers/runc/commit/8781993968fd964ac723ff5f360b6f259e809a3e
- https://github.com/opencontainers/runc/commit/f0b652ea61ff6750a8fcc69865d45a7abf37accf
- https://github.com/opencontainers/runc
- https://security.netapp.com/advisory/ntap-20250221-0008
- http://www.openwall.com/lists/oss-security/2024/09/03/1
