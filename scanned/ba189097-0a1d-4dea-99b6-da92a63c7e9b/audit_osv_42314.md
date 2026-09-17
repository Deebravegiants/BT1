# [M] Apache Tika: Arbitrary Local File Read in ISArchiveParser

## Summary
Severity: Medium
Advisory: CVE-2026-66755
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/AU:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-66755
Type: osv

## Details
Relative Path Traversal in the ISA-Tab parser in Apache Software Foundation Apache Tika from 1.8 through 3.3.1, and 4.0.0-alpha-1, allows an attacker who can place files in a directory that the application subsequently parses to read arbitrary files accessible to the Tika process and have their contents emitted into the extracted text output, via a "Study Assay File Name" value in the ISA-Tab investigation file that traverses outside the dataset directory. Users are recommended to upgrade to version 3.3.2 or 4.0.0-beta-1, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/30/23
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66755.json
- https://lists.apache.org/thread/0hcctcp9s5lxgq2ookp4o6chltk99f8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-66755
