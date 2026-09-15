# [M] CVE-2022-3592

## Summary
Severity: Medium
Advisory: CVE-2022-3592
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2022-3592
Type: osv

## Details
A symlink following vulnerability was found in Samba, where a user can create a symbolic link that will make 'smbd' escape the configured share path. This flaw allows a remote user with access to the exported part of the file system under a share via SMB1 unix extensions or NFS to create symlinks to files outside the 'smbd' configured share path and gain access to another restricted server's filesystem.

## References
- https://access.redhat.com/security/cve/CVE-2022-3592
- https://www.samba.org/samba/security/CVE-2022-3592.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3592.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3592
- https://security.gentoo.org/glsa/202309-06
- https://bugzilla.redhat.com/show_bug.cgi?id=2137776
