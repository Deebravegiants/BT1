# [M] cym1102 nginxWebUI reload exec deserialization

## Summary
Severity: Medium
Advisory: CVE-2024-3740
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-13
Source: https://osv.dev/vulnerability/CVE-2024-3740
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in cym1102 nginxWebUI up to 3.9.9. This issue affects the function exec of the file /adminPage/conf/reload. The manipulation of the argument nginxExe leads to deserialization. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-260579.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3740.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3740
- https://vuldb.com/?id.260579
- https://vuldb.com/?submit.311216
- https://github.com/cym1102/nginxWebUI/issues/138
- https://vuldb.com/?ctiid.260579
- https://github.com/cym1102/nginxWebUI/files/14818455/nginxwebui.rce.3.9.9.pdf
