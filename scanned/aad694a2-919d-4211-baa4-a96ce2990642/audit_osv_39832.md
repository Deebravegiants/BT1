# [H] blobs.yaml Path Traversal Allows File Writes

## Summary
Severity: High
Advisory: CVE-2026-47826
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-47826
Type: osv

## Details
The blobs.yml path key traversal vulnerability in the BOSH CLI tool allows an attacker to write arbitrary files and exfiltrate sensitive information.
Affected versions: BOSH CLI tool versions prior to v7.10.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47826.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47826
- https://www.cloudfoundry.org/blog/cve-2026-47826-blobs-yaml-path-traversal-allows-file-writes/
