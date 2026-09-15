# [C] Apache Kyuubi: REST batch multipart upload path traversal allows controlled file write

## Summary
Severity: Critical
Advisory: CVE-2026-52680
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-52680
Type: osv

## Details
Apache Kyuubi REST batch multipart upload handling uses the client-supplied multipart filename when creating a temporary uploaded resource. A remote attacker who can access the REST batch upload endpoint can provide path traversal sequences in the filename and cause the Kyuubi server process to write controlled content outside the intended upload directory, subject to filesystem permissions.


This issue affects Apache Kyuubi: from 1.7.0 through 1.11.1.

Users are recommended to upgrade to version 1.12.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/30/5
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52680.json
- https://lists.apache.org/thread/b0qx2v8k5v4rrqsh53pb146t7so0lmrk
- https://nvd.nist.gov/vuln/detail/CVE-2026-52680
