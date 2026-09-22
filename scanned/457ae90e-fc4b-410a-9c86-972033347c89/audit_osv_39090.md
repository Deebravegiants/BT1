# [H] Outline: Zip Extraction Path Escape via PATH_MAX Truncation in Collection Import

## Summary
Severity: High
Advisory: CVE-2026-43888
Aliases: GHSA-hw32-2v7j-mgqc
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43888
Type: osv

## Details
Outline is a service that allows for collaborative documentation. Prior to 1.7.0, ZipHelper.extract computes the extraction path for each entry by passing a full filesystem path through trimFileAndExt, a filename helper that calls path.basename on its input when truncating. When a zip entry's nested path is long enough to push the joined filesystem path over MAX_PATH_LENGTH (4096 bytes), trimFileAndExt silently drops all directory components and returns a bare filename. fs.createWriteStream then opens the file relative to the process working directory instead of inside the extraction sandbox, and the escaped file persists after import cleanup because cleanupExtractedData only removes the temporary extraction directory. This vulnerability is fixed in 1.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43888.json
- https://github.com/outline/outline/security/advisories/GHSA-hw32-2v7j-mgqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-43888
