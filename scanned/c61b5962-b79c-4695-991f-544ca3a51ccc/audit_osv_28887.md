# [M] cym1102 nginxWebUI addOver findCountByQuery path traversal

## Summary
Severity: Medium
Advisory: CVE-2024-3737
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-13
Source: https://osv.dev/vulnerability/CVE-2024-3737
Type: osv

## Details
A vulnerability was found in cym1102 nginxWebUI up to 3.9.9. It has been rated as critical. Affected by this issue is the function findCountByQuery of the file /adminPage/www/addOver. The manipulation of the argument dir leads to path traversal. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. The identifier of this vulnerability is VDB-260576.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3737.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3737
- https://vuldb.com/?id.260576
- https://github.com/cym1102/nginxWebUI/issues/138
- https://vuldb.com/?ctiid.260576
- https://github.com/cym1102/nginxWebUI/files/14818455/nginxwebui.rce.3.9.9.pdf
