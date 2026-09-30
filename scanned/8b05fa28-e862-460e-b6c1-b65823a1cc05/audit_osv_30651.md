# [M] Nanopb does not release memory on error return when using PB_DECODE_DELIMITED

## Summary
Severity: Medium
Advisory: CVE-2024-53984
Aliases: GHSA-xwqq-qxmw-hj5r
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53984
Type: osv

## Details
Nanopb is a small code-size Protocol Buffers implementation.  When the compile time option PB_ENABLE_MALLOC is enabled, the message contains at least one field with FT_POINTER field type, custom stream callback is used with unknown stream length. and the pb_decode_ex() function is used with flag PB_DECODE_DELIMITED, then the pb_decode_ex() function does not automatically call pb_release(), like is done for other failure cases. This could lead to memory leak and potential denial-of-service. This vulnerability is fixed in 0.4.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53984.json
- https://github.com/nanopb/nanopb/security/advisories/GHSA-xwqq-qxmw-hj5r
- https://nvd.nist.gov/vuln/detail/CVE-2024-53984
- https://github.com/nanopb/nanopb/commit/2b86c255aa52250438d5aba124d0e86db495b378
