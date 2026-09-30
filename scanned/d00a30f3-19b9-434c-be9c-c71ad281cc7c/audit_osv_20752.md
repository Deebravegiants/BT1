# [M] CVE-2021-3667

## Summary
Severity: Medium
Advisory: CVE-2021-3667
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-3667
Type: osv

## Details
An improper locking issue was found in the virStoragePoolLookupByTargetPath API of libvirt. It occurs in the storagePoolLookupByTargetPath function where a locked virStoragePoolObj object is not properly released on ACL permission failure. Clients connecting to the read-write socket with limited ACL permissions could use this flaw to acquire the lock and prevent other users from accessing storage pool/volume APIs, resulting in a denial of service condition. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://security.gentoo.org/glsa/202210-06
- https://security.netapp.com/advisory/ntap-20220331-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=1986094
- https://gitlab.com/libvirt/libvirt/-/commit/447f69dec47e1b0bd15ecd7cd49a9fd3b050fb87
- https://libvirt.org/git/?p=libvirt.git%3Ba=commit%3Bh=447f69dec47e1b0bd15ecd7cd49a9fd3b050fb87
