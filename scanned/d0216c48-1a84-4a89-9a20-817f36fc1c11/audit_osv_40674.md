# [M] Path Traversal in jupyter/jupyter

## Summary
Severity: Medium
Advisory: CVE-2026-5422
Aliases: GHSA-gf7q-q4j7-hp7c, PYSEC-2026-2532
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-5422
Type: osv

## Details
A path traversal vulnerability exists in jupyter-server version 2.17.0 due to an incorrect root directory boundary check in the _get_os_path() function within jupyter_server/services/contents/fileio.py. The check uses startswith(root) without appending a trailing path separator, allowing sibling directories with names starting with the same prefix as root_dir to bypass the check. Additionally, the to_os_path() function in utils.py does not strip ".." from path parts, enabling traversal sequences to bypass the vulnerable check. This vulnerability can lead to unauthorized read/write access to files in sibling directories, potentially exposing sensitive data in shared hosting environments.

## References
- https://huntr.com/bounties/24a36953-6490-466f-8cb2-a90d1ca56e0f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5422.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5422
