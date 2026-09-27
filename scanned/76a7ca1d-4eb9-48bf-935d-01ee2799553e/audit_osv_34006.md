# [H] CVE-2025-53603

## Summary
Severity: High
Advisory: CVE-2025-53603
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-05
Source: https://osv.dev/vulnerability/CVE-2025-53603
Type: osv

## Details
In Alinto SOPE SOGo 2.0.2 through 5.12.2, sope-core/NGExtensions/NGHashMap.m allows a NULL pointer dereference and SOGo crash via a request in which a parameter in the query string is a duplicate of a parameter in the POST body.

## References
- http://www.openwall.com/lists/oss-security/2025/07/05/1
- https://github.com/Alinto/sope/blob/3146fbdb6ff3314e37e5c3682deeeef7d0f32064/sope-core/NGExtensions/NGHashMap.m#L790
- https://github.com/Alinto/sope/compare/SOGo-2.0.1...SOGo-2.0.2
- https://lists.debian.org/debian-lts-announce/2025/08/msg00001.html
- https://www.openwall.com/lists/oss-security/2025/07/02/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53603.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53603
- https://github.com/Alinto/sope/commit/280104e45c20519ac4849ebf8bca114d91383543
- https://github.com/Alinto/sope/pull/69
