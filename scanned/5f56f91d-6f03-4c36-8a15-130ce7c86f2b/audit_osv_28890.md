# [H] cym1102 nginxWebUI saveCmd handlePath certificate validation

## Summary
Severity: High
Advisory: CVE-2024-3738
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-13
Source: https://osv.dev/vulnerability/CVE-2024-3738
Type: osv

## Details
A vulnerability classified as critical has been found in cym1102 nginxWebUI up to 3.9.9. This affects the function handlePath of the file /adminPage/conf/saveCmd. The manipulation of the argument nginxPath leads to improper certificate validation. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. The identifier VDB-260577 was assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3738.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3738
- https://vuldb.com/?id.260577
- https://github.com/cym1102/nginxWebUI/issues/138
- https://vuldb.com/?ctiid.260577
- https://github.com/cym1102/nginxWebUI/files/14818455/nginxwebui.rce.3.9.9.pdf
