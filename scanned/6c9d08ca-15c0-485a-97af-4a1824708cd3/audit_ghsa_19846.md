# [H] zip Incorrectly Canonicalizes Paths during Archive Extraction Leading to Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-94vh-gphv-8pm8
CVE: CVE-2025-29787
CWE: CWE-180, CWE-22, CWE-61
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-03-17
Source: https://github.com/advisories/GHSA-94vh-gphv-8pm8
Type: github-advisory

## Affected
- crates.io: `zip` — affected >=1.3.0 <2.3.0

## Details
### Summary


In the archive extraction routine of affected versions of the `zip` crate, symbolic links earlier in the archive are allowed to be used for later files in the archive without validation of the final canonicalized path, allowing maliciously crafted archives to overwrite arbitrary files in the file system when extracted.

### Details

This is a variant of the [zip-slip](https://github.com/snyk/zip-slip-vulnerability) vulnerability, we can make the extraction logic step outside of the target directory by creating a symlink to the parent directory and then extracting further files through that symlink.

The documentation of the [`::zip::read::ZipArchive::extract`] method is in my opinion implying this should not happen:

> "Paths are sanitized with ZipFile::enclosed_name." ...
> [`::zip::read::FileOptions::enclosed_name`] ... is resistant to path-based exploits ... can’t resolve to a path outside the current directory.


Most archive software either decline to extract symlinks that traverse out of the directory or defer creation of symlinks after all files have been created to prevent unexpected behavior when later entries depend on earlier symbolic link entries.

### PoC

https://gist.github.com/eternal-flame-AD/bf71ef4f6828e741eb12ce7fd47b7b85

### Impact

Users who extract untrusted archive files using the following high-level API method may be affected and critical files on the system may be overwritten with arbitrary file permissions, which can potentially lead to code execution.

- zip::unstable::stream::ZipStreamReader::extract
- zip::read::ZipArchive::extract

## References
- https://github.com/zip-rs/zip2/security/advisories/GHSA-94vh-gphv-8pm8
- https://nvd.nist.gov/vuln/detail/CVE-2025-29787
- https://github.com/zip-rs/zip2/commit/a2e062f37066c3b12860a32eb1cb44856cfb7afe
- https://gist.github.com/eternal-flame-AD/bf71ef4f6828e741eb12ce7fd47b7b85
- https://github.com/zip-rs/zip2
- https://github.com/zip-rs/zip2/releases/tag/v2.3.0
