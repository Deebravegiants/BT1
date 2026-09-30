# [M] Path traversal in NotebookRepo note and folder path composition

## Summary
Severity: Medium
Advisory: CVE-2026-44615
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-44615
Type: osv

## Details
Path traversal vulnerability in Apache Zeppelin. When FileSystemNotebookRepo is configured, an authenticated attacker with permission to rename a note, or access to folder operations, could supply traversal segments in note or folder paths.                   Zeppelin composed these values into filesystem paths using the server's filesystem or Hadoop identity without ensuring that the result remained under the configured notebook directory. This could allow notebook files or directories to be moved,                   written, or deleted outside the notebook root. This issue affects Apache Zeppelin versions 0.9.0 through 0.12.0. Users are recommended to upgrade to version 0.12.1, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/30/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44615.json
- https://lists.apache.org/thread/ps1f0symnyxzq8c2dc3244v051jcwp40
- https://nvd.nist.gov/vuln/detail/CVE-2026-44615
- https://github.com/apache/zeppelin/pull/5227
- https://github.com/apache/zeppelin/pull/5248
