# [M] GPAC reframe_mp3.c mp3_dmx_process heap-based overflow

## Summary
Severity: Medium
Advisory: CVE-2023-0841
Aliases: GHSA-w52x-cp47-xhhw
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-02-15
Source: https://osv.dev/vulnerability/CVE-2023-0841
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in GPAC 2.3-DEV-rev40-g3602a5ded. This issue affects the function mp3_dmx_process of the file filters/reframe_mp3.c. The manipulation leads to heap-based buffer overflow. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-221087.

## References
- https://github.com/gpac/gpac/releases/tag/v2.2.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0841.json
- https://github.com/advisories/GHSA-w52x-cp47-xhhw
- https://nvd.nist.gov/vuln/detail/CVE-2023-0841
- https://vuldb.com/?id.221087
- https://github.com/gpac/gpac/issues/2396
- https://vuldb.com/?ctiid.221087
- https://github.com/gpac/gpac/commit/851560e3dc8155d45ace4b0d77421f241ed71dc4
- https://github.com/qianshuidewajueji/poc/blob/main/gpac/mp3_dmx_process_poc3
