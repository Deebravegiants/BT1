# [C] Instance template path traversal allows arbitrary host file write as root

## Summary
Severity: Critical
Advisory: CVE-2026-66897
Aliases: GHSA-q39m-8fx9-42fv
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-66897
Type: osv

## Details
A path traversal vulnerability in LXD's instance template processing allows an attacker with container edit permissions, or any user launching a crafted image, to overwrite arbitrary files on the host system as root. When processing target template paths specified in metadata.yaml, LXD validates the path against a confined os.Root directory handle but subsequently opens and creates the file using os.Create with an unconfined string path. This discrepancy between path resolution checks and file creation allows an attacker to escape directory confinement, overwrite root-owned host files, and achieve host root code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66897.json
- https://github.com/canonical/lxd/security/advisories/GHSA-q39m-8fx9-42fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-66897
- https://github.com/canonical/lxd
