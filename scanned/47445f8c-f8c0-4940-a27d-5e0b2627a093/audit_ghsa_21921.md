# [M] Symbolic links in an unpacking routine may enable attackers to read and/or write to arbitrary locations in dbdeployer

## Summary
Severity: Medium
Advisory: GHSA-47wr-426j-fr82
CVE: CVE-2020-26277
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-47wr-426j-fr82
Type: github-advisory

## Affected
- Go: `github.com/datacharmer/dbdeployer` — affected >=0 <1.58.2

## Details
### Impact
_Users unpacking a tarball through dbdeployer may use a maliciously packaged tarball that contains symlinks to files external to the target. In such scenario, an attacker could induce dbdeployer to write into a system file, thus altering the computer defences._

### Mitigating factors
For the attach to succeed, the following factors need to contribute:

* The user is logged in as root. While dbdeployer is usable as root, it was designed to run as unprivileged user.
*  The user has taken a tarball from a non secure source, without testing the checksum. When the tarball is retrieved through dbdeployer, the checksum is compared before attempting to unpack.

### Analysis

An attacker could inject a symbolic link into the tarball, so that a file could result into `fake_file -> /etc/passwd` or some equally  important file.
As it is now, dbdeployer would create the symlink as defined, with a local file `fake_file` linked to `/etc/passwd`. The danger here is that any process with the privileges to write to both `fake_file` and `/etc/passwd` could overwrite the system file. Even without malicious intent, this could result in the system to become unusable.
As noted above, the user must have write privileges to the target file to do the damage.

### Remedies

It has been suggested that the extract procedure use `filepath.EvalSymlinks` to determine whether the target is within the extraction directory. Unfortunately, this approach is unavailable in this context, because it would prevent legitimate patterns from being carried out.
A simple case is a file `mysql-8.0.22-macos10.15-x86_64/bin/libprotobuf-lite.3.11.4.dylib` with a linkName `../lib/libprotobuf-lite.3.11.4.dylib`, if the linked file has not been created yet, `filepath.EvalSymlinks` would fail, as it acts on existing files only.

An alternative method is comparing the depth (how many directories) of the file name with the depth of the link name. If the link name has a higher depth than the local file, we block the operation with an appropriate error:

```
Unpacking tarball exploit/mysql-8.0.22-macos10.15-x86_64.tar.gz to $HOME/opt/mysql/test8.0.22
......
link '../../../../../../../../../../etc' points outside target directory

exit status 1
```
As an additional fortifier, we can check whether the link points to an existing file, calculate its absolute name, and compare it with the absolute name of the extraction directory. A link to a full path (such as `/etc/passwd`) would fail this test, and trigger an error.

The same check can be applied to a link to a non existing file with absolute path.

### Patches

Patched in release 1.58.2

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [dbdeployer](https://github.com/datacharmer/dbdeployer)

## References
- https://github.com/datacharmer/dbdeployer/security/advisories/GHSA-47wr-426j-fr82
- https://nvd.nist.gov/vuln/detail/CVE-2020-26277
- https://github.com/datacharmer/dbdeployer/commit/548e256c1de2f99746e861454e7714ec6bc9bb10
