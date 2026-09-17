# [M] CVE-2021-44269

## Summary
Severity: Medium
Advisory: CVE-2021-44269
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-44269
Type: osv

## Details
An out of bounds read was found in Wavpack 5.4.0 in processing *.WAV files. This issue triggered in function WavpackPackSamples of file src/pack_utils.c, tainted variable cnt is too large, that makes pointer sptr read beyond heap bound.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2CZUFTX3J4Y4OSRITG4PXCI7NRVFDYVQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A5B7L26LA6KGX7YH6SWD5CSBNWKV5MBO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CRZWZKEEABCLVXZEXQZBIT3ZKLIXVFF5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I54NXQZELBF42OL4KQZJJRAYZX7IPZXP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SQKOOJRI2VAPYS3652HVDXON723HTXBP/
- https://github.com/dbry/WavPack/issues/110
