# [M] sslh Packet Dumping probe.c hexdump format string

## Summary
Severity: Medium
Advisory: CVE-2022-4639
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-12-21
Source: https://osv.dev/vulnerability/CVE-2022-4639
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in sslh. This issue affects the function hexdump of the file probe.c of the component Packet Dumping Handler. The manipulation of the argument msg_info leads to format string. The attack may be initiated remotely. The name of the patch is b19f8a6046b080e4c2e28354a58556bb26040c6f. It is recommended to apply a patch to fix this issue. The identifier VDB-216497 was assigned to this vulnerability.

## References
- https://vuldb.com/?id.216497
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4639.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4639
- https://github.com/yrutschle/sslh/commit/b19f8a6046b080e4c2e28354a58556bb26040c6f
- https://github.com/yrutschle/sslh/pull/353
