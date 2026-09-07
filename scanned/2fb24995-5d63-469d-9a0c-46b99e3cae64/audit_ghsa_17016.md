# [M] Moby (Docker Engine) started with non-empty inheritable Linux process capabilities

## Summary
Severity: Medium
Advisory: GHSA-2mm7-x5h6-5pvq
CVE: CVE-2022-24769
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-2mm7-x5h6-5pvq
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <20.10.14
- Go: `github.com/docker/docker` — affected >=0 <20.10.14

## Details
### Impact

A bug was found in Moby (Docker Engine) where containers were incorrectly started with non-empty inheritable Linux process capabilities, creating an atypical Linux environment and enabling programs with inheritable file capabilities to elevate those capabilities to the permitted set during `execve(2)`.  Normally, when executable programs have specified permitted file capabilities, otherwise unprivileged users and processes can execute those programs and gain the specified file capabilities up to the bounding set.  Due to this bug, containers which included executable programs with inheritable file capabilities allowed otherwise unprivileged users and processes to additionally gain these inheritable file capabilities up to the container's bounding set.  Containers which use Linux users and groups to perform privilege separation inside the container are most directly impacted.

This bug did not affect the container security sandbox as the inheritable set never contained more capabilities than were included in the container's bounding set.


### Patches

This bug has been fixed in Moby (Docker Engine) 20.10.14.  Users should update to this version as soon as possible.  Running containers should be stopped, deleted, and recreated for the inheritable capabilities to be reset.

This fix changes Moby (Docker Engine) behavior such that containers are started with a more typical Linux environment.  Refer to `capabilities(7)` for a description of how capabilities work.  Note that permitted file capabilities continue to allow for privileges to be raised up to the container's bounding set and that processes may add capabilities to their own inheritable set up to the container's bounding set per the rules described in the manual page.  In all cases the container's bounding set provides an upper bound on the capabilities that can be assumed and provides for the container security sandbox.

### Workarounds

The entrypoint of a container can be modified to use a utility like `capsh(1)` to drop inheritable capabilities prior to the primary process starting.

### Credits

The Moby project would like to thank [Andrew G. Morgan](https://github.com/AndrewGMorgan) for responsibly disclosing this issue in accordance with the [Moby security policy](https://github.com/moby/moby/blob/master/SECURITY.md).

### For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/moby/moby/issues/new)
* Email us at [security@docker.com](mailto:security@docker.com) if you think you’ve found a security bug

## References
- https://github.com/moby/moby/security/advisories/GHSA-2mm7-x5h6-5pvq
- https://nvd.nist.gov/vuln/detail/CVE-2022-24769
- https://github.com/moby/moby/commit/2bbc786e4c59761d722d2d1518cd0a32829bc07f
- https://github.com/moby/moby/commit/7f375bcff41ce672cd61e9a31f3eeb2966e3dbe1
- https://www.debian.org/security/2022/dsa-5162
- https://security.gentoo.org/glsa/202401-31
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HQCVS7WBFSTKJFNX5PGDRARMTOFWV2O7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HIMAHZ6AUIKN7AX26KHZYBXVECIOVWBH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FPOJUJZXGMIVKRS4QR75F6OIXNQ6LDBL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A5FQJ3MLFSEKQYCFPFZIKYGBXPZUJFVY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/A5AFKOQ5CE3CEIULWW4FLQKHFFU6FSYG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6PMQKCAPK2AR3DCYITJYMMNBEGQBGLCC
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HQCVS7WBFSTKJFNX5PGDRARMTOFWV2O7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HIMAHZ6AUIKN7AX26KHZYBXVECIOVWBH
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FPOJUJZXGMIVKRS4QR75F6OIXNQ6LDBL
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A5FQJ3MLFSEKQYCFPFZIKYGBXPZUJFVY
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A5AFKOQ5CE3CEIULWW4FLQKHFFU6FSYG
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6PMQKCAPK2AR3DCYITJYMMNBEGQBGLCC
- https://github.com/moby/moby/releases/tag/v20.10.14
- https://github.com/moby/moby
