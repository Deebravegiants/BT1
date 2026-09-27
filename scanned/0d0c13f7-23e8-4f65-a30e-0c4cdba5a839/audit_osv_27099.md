# [M] Fileserver crash and possible information leak on StoreACL/FetchACL

## Summary
Severity: Medium
Advisory: CVE-2024-10396
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-10396
Type: osv

## Details
An authenticated user can provide a malformed ACL to the fileserver's StoreACL RPC, causing the fileserver to crash, possibly expose uninitialized memory, and possibly store garbage data in the audit log. Malformed ACLs provided in responses to client FetchACL RPCs can cause client processes to crash and possibly expose uninitialized memory into other ACLs stored on the server.

## References
- https://github.com/openafs/openafs/
- https://lists.debian.org/debian-lts-announce/2025/05/msg00019.html
- https://www.openafs.org/pages/security/OPENAFS-SA-2024-002.txt
- https://www.openafs.org/security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10396.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10396
