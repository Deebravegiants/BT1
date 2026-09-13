# [M] GNU Tar through 1.35 allows file overwrite via directory traversal in crafted TAR archives, with a...

## Summary
Severity: Medium
Advisory: JLSEC-2025-197
Ecosystem: Julia
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:N/I:L/A:L)
Published: 2025-11-03
Source: https://osv.dev/vulnerability/JLSEC-2025-197
Type: osv

## Affected
- Julia: `Tar_jll` — affected >=0 <1.35.0+0

## Details
GNU Tar through 1.35 allows file overwrite via directory traversal in crafted TAR archives, with a certain two-step process. First, the victim must extract an archive that contains a `../` symlink to a critical directory. Second, the victim must extract an archive that contains a critical file, specified via a relative pathname that begins with the symlink name and ends with that critical file's name. Here, the extraction follows the symlink and overwrites the critical file. This bypasses the protection mechanism of "Member name contains '`..`'" that would occur for a single TAR archive that attempted to specify the critical file via a `../` approach. For example, the first archive can contain "`x -> ../../../../../home/victim/.ssh`" and the second archive can contain `x/authorized_keys`. This can affect server applications that automatically extract any number of user-supplied TAR archives, and were relying on the blocking of traversal. This can also affect software installation processes in which "tar xf" is run more than once (e.g., when installing a package can automatically install two dependencies that are set up as untrusted tarballs instead of official packages). NOTE: the official GNU Tar manual has an otherwise-empty directory for each "tar xf" in its Security Rules of Thumb; however, third-party advice leads users to run "tar xf" more than once into the same directory.

## References
- http://www.openwall.com/lists/oss-security/2025/11/01/6
- https://github.com/i900008/vulndb/blob/main/Gnu_tar_vuln.md
- https://lists.gnu.org/archive/html/bug-tar/2025-08/msg00012.html
- https://www.gnu.org/software/tar/
- https://www.gnu.org/software/tar/manual/html_node/Integrity.html
- https://www.gnu.org/software/tar/manual/html_node/Security-rules-of-thumb.html
