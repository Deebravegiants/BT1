# [H] Local Git clone may hardlink arbitrary user-readable files into the new repository's "objects/" directory

## Summary
Severity: High
Advisory: BIT-git-2024-32021
Aliases: CVE-2024-32021, GHSA-mvxm-9j2h-qjx7
Ecosystem: Bitnami
Published: 2024-05-24
Source: https://osv.dev/vulnerability/BIT-git-2024-32021
Type: osv

## Affected
- Bitnami: `git` — affected >=2.45.0 <2.45.1

## Details
Git is a revision control system. Prior to versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4, when cloning a local source repository that contains symlinks via the filesystem, Git may create hardlinks to arbitrary user-readable files on the same filesystem as the target repository in the `objects/` directory. Cloning a local repository over the filesystem may creating hardlinks to arbitrary user-owned files on the same filesystem in the target Git repository's `objects/` directory. When cloning a repository over the filesystem (without explicitly specifying the `file://` protocol or `--no-local`), the optimizations for local cloning
will be used, which include attempting to hard link the object files instead of copying them. While the code includes checks against symbolic links in the source repository, which were added during the fix for CVE-2022-39253, these checks can still be raced because the hard link operation ultimately follows symlinks. If the object on the filesystem appears as a file during the check, and then a symlink during the operation, this will allow the adversary to bypass the check and create hardlinks in the destination objects directory to arbitrary, user-readable files. The problem has been patched in versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4.

## References
- https://github.com/git/git/security/advisories/GHSA-mvxm-9j2h-qjx7
- http://www.openwall.com/lists/oss-security/2024/05/14/2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S4CK4IYTXEOBZTEM5K3T6LWOIZ3S44AR/
- https://lists.debian.org/debian-lts-announce/2024/06/msg00018.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-32021
- https://lists.debian.org/debian-lts-announce/2024/09/msg00009.html
