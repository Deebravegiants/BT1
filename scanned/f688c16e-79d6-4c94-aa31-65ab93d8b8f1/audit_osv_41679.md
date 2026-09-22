# [M] Malcolm's Path Traversal in Archive Extraction Allows Arbitrary Directory Creation

## Summary
Severity: Medium
Advisory: CVE-2026-63134
Aliases: GHSA-65mm-vgrw-vqx4
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-63134
Type: osv

## Details
Malcolm is a network traffic analysis tool suite. Prior to version 26.07.0, `safe-extract.py` protects file extraction with libarchive's secure flags, but creates directory entries with a raw `os.makedirs(os.path.join(dest, entry.pathname))` that has no traversal protection. An uploaded malicious archive containing a directory entry with a `../` sequence or an absolute path causes the filebeat processing container to create directories outside the intended extraction directory. Version 26.07.0 fixes the issue.

## References
- https://github.com/cisagov/Malcolm/releases/tag/v26.07.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63134.json
- https://github.com/cisagov/Malcolm/security/advisories/GHSA-65mm-vgrw-vqx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-63134
