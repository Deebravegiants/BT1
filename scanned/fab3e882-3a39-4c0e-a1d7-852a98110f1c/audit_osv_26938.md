# [M] jeecgboot JimuReport image path traversal

## Summary
Severity: Medium
Advisory: CVE-2023-6307
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-6307
Type: osv

## Details
A vulnerability classified as critical was found in jeecgboot JimuReport up to 1.6.1. Affected by this vulnerability is an unknown functionality of the file /download/image. The manipulation of the argument imageUrl leads to relative path traversal. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. The identifier VDB-246133 was assigned to this vulnerability. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6307.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6307
- https://vuldb.com/?id.246133
- https://vuldb.com/?ctiid.246133
- https://github.com/N0b1e6/exp/blob/main/README.md
