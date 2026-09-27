# [M] cym1102 nginxWebUI upload os command injection

## Summary
Severity: Medium
Advisory: CVE-2024-3739
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-13
Source: https://osv.dev/vulnerability/CVE-2024-3739
Type: osv

## Details
A vulnerability classified as critical was found in cym1102 nginxWebUI up to 3.9.9. This vulnerability affects unknown code of the file /adminPage/main/upload. The manipulation of the argument file leads to os command injection. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. VDB-260578 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3739.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3739
- https://vuldb.com/?id.260578
- https://github.com/cym1102/nginxWebUI/issues/138
- https://vuldb.com/?ctiid.260578
- https://github.com/cym1102/nginxWebUI/files/14818455/nginxwebui.rce.3.9.9.pdf
