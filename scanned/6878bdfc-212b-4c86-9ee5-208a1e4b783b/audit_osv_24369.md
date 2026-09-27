# [M] MuYuCMS index.php path traversal

## Summary
Severity: Medium
Advisory: CVE-2023-1002
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-02-24
Source: https://osv.dev/vulnerability/CVE-2023-1002
Type: osv

## Details
A vulnerability, which was classified as problematic, has been found in MuYuCMS 2.2. This issue affects some unknown processing of the file index.php. The manipulation of the argument file_path leads to path traversal. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-221735.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1002.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1002
- https://vuldb.com/?id.221735
- https://github.com/MuYuCMS/MuYuCMS/issues/3
- https://vuldb.com/?ctiid.221735
