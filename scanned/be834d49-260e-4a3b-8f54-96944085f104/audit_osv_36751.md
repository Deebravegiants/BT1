# [H] iccDEV vulnerable to Heap Buffer Overflow in CIccIO::WriteUInt16Float()

## Summary
Severity: High
Advisory: CVE-2026-25582
Aliases: GHSA-46hq-fphp-jggf
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25582
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.3, there is a heap buffer overflow (read) vulnerability in CIccIO::WriteUInt16Float() when converting malformed XML to ICC profiles via iccFromXml tool. This issue has been patched in version 2.3.1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25582.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-46hq-fphp-jggf
- https://nvd.nist.gov/vuln/detail/CVE-2026-25582
- https://github.com/InternationalColorConsortium/iccDEV/issues/559
- https://github.com/InternationalColorConsortium/iccDEV/commit/b5e5dd238f609ec1a4efb25674e7fa4bd29d894a
- https://github.com/InternationalColorConsortium/iccDEV/pull/561
