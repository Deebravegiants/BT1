# [M] CVE-2016-4536

## Summary
Severity: Medium
Advisory: CVE-2016-4536
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-4536
Type: osv

## Details
The client in OpenAFS before 1.6.17 does not properly initialize the (1) AFSStoreStatus, (2) AFSStoreVolumeStatus, (3) VldbListByAttributes, and (4) ListAddrByAttributes structures, which might allow remote attackers to obtain sensitive memory information by leveraging access to RPC call traffic.

## References
- https://lists.openafs.org/pipermail/openafs-announce/2016/000496.html
- https://www.openafs.org/dl/openafs/1.6.17/RELNOTES-1.6.17
- https://www.openafs.org/pages/security/OPENAFS-SA-2016-002.txt
