# [M] Improper input validation in umoci

## Summary
Severity: Medium
Advisory: GHSA-9m95-8hx6-7p9v
CVE: CVE-2021-29136
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-9m95-8hx6-7p9v
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/umoci` — affected >=0 <0.4.7

## Details
### Impact

umoci 0.4.6 and earlier can be tricked into modifying host files by
creating a malicious layer that has a symlink with the name "." (or
"/"). Because umoci deletes inodes if they change types, this results in
the rootfs directory being replaced with an attacker-controlled symlink.
Subsequent image layers will then be applied on top of the target of the
symlink (which could be any directory on the host filesystem the user
running umoci has access to).

While umoci does have defences against symlink-based attacks, they are
all implemented by resolving things relative to the rootfs directory --
if the rootfs itself is a symlink, umoci resolves it first.

This vulnerability affects both "umoci unpack" and "umoci raw unpack".

### Patches
This issue has been patched in umoci 0.4.7, see the references section
for the specific commit which fixed this vulnerability.

### Workarounds
Note that if you use umoci as an unprivileged user (using the --rootless
flag) then umoci will not be able to overwrite any files that your user
doesn't have access to. Other possible mitigations are to run umoci
under an LSM profile such as AppArmor or SELinux to restrict the level
of access it has outside of container image directories.

### References
* [oss-security public disclosure](https://www.openwall.com/lists/oss-security/2021/04/06/2)
* [patch](https://github.com/opencontainers/umoci/commit/d9efc31daf2206f7d3fdb839863cf7a576a2eb57)

### Credits
Thanks to Robin Peraglie from Cure53 for discovering and reporting this
vulnerability.

### For more information

If you have any questions or comments about this advisory
* Open an issue in <https://github.com/opencontainers/umoci>.
* Email us at <security@opencontainers.org>.

## References
- https://github.com/opencontainers/umoci/security/advisories/GHSA-9m95-8hx6-7p9v
- https://nvd.nist.gov/vuln/detail/CVE-2021-29136
- https://github.com/opencontainers/umoci/commit/d9efc31daf2206f7d3fdb839863cf7a576a2eb57
- http://www.openwall.com/lists/oss-security/2021/04/06/2
