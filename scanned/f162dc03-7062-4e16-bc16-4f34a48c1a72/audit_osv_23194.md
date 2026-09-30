# [M] bspkrs MCPMappingViewer ZIP File RemoteZipHandler.java extractZip path traversal

## Summary
Severity: Medium
Advisory: CVE-2022-4494
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-4494
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in bspkrs MCPMappingViewer. Affected by this issue is the function extractZip of the file src/main/java/bspkrs/mmv/RemoteZipHandler.java of the component ZIP File Handler. The manipulation leads to path traversal. The attack may be launched remotely. The name of the patch is 6e602746c96b4756c271d080dae7d22ad804a1bd. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-215804.

## References
- https://vuldb.com/?id.215804
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4494.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4494
- https://github.com/bspkrs/MCPMappingViewer/commit/6e602746c96b4756c271d080dae7d22ad804a1bd
