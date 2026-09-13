# [H] CVE-2013-20001

## Summary
Severity: High
Advisory: CVE-2013-20001
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-12
Source: https://osv.dev/vulnerability/CVE-2013-20001
Type: osv

## Details
An issue was discovered in OpenZFS through 2.0.3. When an NFS share is exported to IPv6 addresses via the sharenfs feature, there is a silent failure to parse the IPv6 address data, and access is allowed to everyone. IPv6 restrictions from the configuration are not applied.

## References
- https://github.com/openzfs/zfs/issues/1894#issuecomment-30693652
- https://github.com/openzfs/zfs/releases
- https://github.com/openzfs/zfs/issues/1894#issuecomment-30693652
- https://lists.debian.org/debian-lts-announce/2024/03/msg00019.html
