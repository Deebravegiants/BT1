# [C] Path Traversal in TAR Archive Extraction Allows Arbitrary File Write in Pandora

## Summary
Severity: Critical
Advisory: CVE-2026-74764
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74764
Type: osv

## Details
Pandora contains a path traversal vulnerability in its TAR archive extraction functionality. When processing a submitted TAR archive, the extractor passed archive member names directly to Python's tarfile.TarFile.extract() without applying an extraction filter.


An attacker able to submit a specially crafted TAR archive containing malicious member paths, such as paths using ../ sequences or absolute paths, could cause extracted files to be written outside the intended extraction directory. This may allow the attacker to overwrite files accessible to the Pandora worker process and could potentially result in application compromise, arbitrary code execution, or denial of service depending on the files targeted and the privileges of the Pandora process.


The vulnerability is corrected by using Python's filter='data' extraction filter, which rejects or sanitizes dangerous TAR members, including paths that escape the destination directory and unsafe link targets. 


The weakness corresponds to MITRE's general path traversal category, which includes archive extraction cases where attacker-controlled filenames cause files to be written outside the intended directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74764.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74764
- https://github.com/pandora-analysis/pandora/commit/186b58d41e04248a154d274fffb5813e7fa2012e
- https://github.com/pandora-analysis/pandora
