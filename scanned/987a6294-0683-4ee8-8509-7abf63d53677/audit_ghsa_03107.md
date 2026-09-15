# [M] opencontainers runc contains procfs race condition with a shared volume mount

## Summary
Severity: Medium
Advisory: GHSA-fh74-hm69-rqjw
CVE: CVE-2019-19921
CWE: CWE-362, CWE-706
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N/E:U/RL:U/RC:U (CVSS_V3)
Published: 2021-05-27
Source: https://github.com/advisories/GHSA-fh74-hm69-rqjw
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=0 <1.0.0-rc9.0.20200122160610-2fc03cc11c77

## Details
### Impact
By crafting a malicious root filesystem (with `/proc` being a symlink to a directory which was inside a volume shared with another running container), an attacker in control of both containers can trick `runc` into not correctly configuring the container's security labels and not correctly masking paths inside `/proc` which contain potentially-sensitive information about the host (or even allow for direct attacks against the host).

In order to exploit this bug, an untrusted user must be able to spawn custom containers with custom mount configurations (such that a volume is shared between two containers). It should be noted that we consider this to be a fairly high level of access for an untrusted user -- and we do not recommend allowing completely untrusted users to have such degrees of access without further restrictions.

### Specific Go Package Affected
github.com/opencontainers/runc/libcontainer

### Patches
This vulnerability has been fixed in `1.0.0-rc10`. It should be noted that the current fix is effectively a hot-fix, and there are known ways for it to be worked around (such as making the entire root filesystem a shared volume controlled by another container). We recommend that users review their access policies to ensure that untrusted users do not have such high levels of controls over container mount configuration.

### Workarounds
If you are not providing the ability for untrusted users to configure mountpoints for `runc` (or through a higher-level tool such as `docker run -v`) then you are not vulnerable to this issue. This exploit requires fairly complicated levels of access (which are available for some public clouds but are not necessarily available for all deployments).

Additionally, it appears as though it is not possible to exploit this vulnerability through Docker (due to the order of mounts Docker generates). However you should not depend on this, as it may be possible to work around this roadblock.

### Credits
This vulnerability was discovered by Cure53, as part of a third-party security audit.

### For more information
If you have any questions or comments about this advisory:
* [Open an issue](https://github.com/opencontainers/runc/issues/new).
* Email us at [dev@opencontainers.org](mailto:dev@opencontainers.org), or [security@opencontainers.org](mailto:security@opencontainers.org) if you think you've found a security bug.

## References
- https://github.com/opencontainers/runc/security/advisories/GHSA-fh74-hm69-rqjw
- https://nvd.nist.gov/vuln/detail/CVE-2019-19921
- https://github.com/opencontainers/runc/issues/2197
- https://github.com/opencontainers/runc/pull/2190
- https://github.com/opencontainers/runc/pull/2207
- https://github.com/opencontainers/runc/commit/2fc03cc11c775b7a8b2e48d7ee447cb9bef32ad0
- https://usn.ubuntu.com/4297-1
- https://security.gentoo.org/glsa/202003-21
- https://security-tracker.debian.org/tracker/CVE-2019-19921
- https://pkg.go.dev/vuln/GO-2021-0087
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I6BF24VCZRFTYBTT3T7HDZUOTKOTNPLZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FYVE3GB4OG3BNT5DLQHYO4M5SXX33AQ5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FNB2UEDIIJCRQW4WJLZOPQJZXCVSXMLD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DHGVGGMKGZSJ7YO67TGGPFEHBYMS63VF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ANUGDBJ7NBUMSUFZUSKU3ZMQYZ2Z3STN
- https://lists.debian.org/debian-lts-announce/2023/03/msg00023.html
- https://github.com/opencontainers/runc/releases
- https://access.redhat.com/errata/RHSA-2020:0695
- https://access.redhat.com/errata/RHSA-2020:0688
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00018.html
