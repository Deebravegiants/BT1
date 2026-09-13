# [M] CVE-2025-51475

## Summary
Severity: Medium
Advisory: CVE-2025-51475
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-51475
Type: osv

## Details
Arbitrary File Overwrite (AFO) in superagi.controllers.resources.upload in TransformerOptimus SuperAGI 0.0.14 allows remote attackers to overwrite arbitrary files via unsanitised filenames submitted to the file upload endpoint, due to improper handling of directory traversal in os.path.join() and lack of path validation in get_root_input_dir().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51475.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51475
- https://github.com/TransformerOptimus/SuperAGI/pull/1463
- https://github.com/TransformerOptimus/SuperAGI
- https://www.gecko.security/blog/cve-2025-51475
