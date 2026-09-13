# [H] TEST_KEY used in example dcp_tool reference implementation

## Summary
Severity: High
Advisory: CVE-2024-38532
Aliases: GHSA-g85c-rh49-p8cq
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-38532
Type: osv

## Details
The NXP Data Co-Processor (DCP) is a built-in hardware module for specific NXP SoCs¹ that implements a dedicated AES cryptographic engine for encryption/decryption operations. The dcp_tool reference implementation included in the repository selected the test key, regardless of its `-t` argument. This issue has been patched in commit 26a7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38532.json
- https://github.com/usbarmory/mxs-dcp/security/advisories/GHSA-g85c-rh49-p8cq
- https://nvd.nist.gov/vuln/detail/CVE-2024-38532
- https://github.com/usbarmory/mxs-dcp/commit/e5a99cb3d9429e6145495da7d01525c75af426a7
