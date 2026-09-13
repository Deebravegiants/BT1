# [H] CVE-2023-1386

## Summary
Severity: High
Advisory: CVE-2023-1386
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-1386
Type: osv

## Details
A flaw was found in the 9p passthrough filesystem (9pfs) implementation in QEMU. When a local user in the guest writes an executable file with SUID or SGID, none of these privileged bits are correctly dropped. As a result, in rare circumstances, this flaw could be used by malicious users in the guest to elevate their privileges within the guest and help a host local user to elevate privileges on the host.

## References
- https://access.redhat.com/security/cve/CVE-2023-1386
- https://github.com/advisories/GHSA-ppj8-867g-rgjr
- https://security.netapp.com/advisory/ntap-20230831-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2223985
- https://github.com/v9fs/linux/issues/29
