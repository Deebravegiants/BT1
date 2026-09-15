# [M] CVE-2024-39929

## Summary
Severity: Medium
Advisory: CVE-2024-39929
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2024-07-04
Source: https://osv.dev/vulnerability/CVE-2024-39929
Type: osv

## Details
Exim through 4.97.1 misparses a multiline RFC 2231 header filename, and thus remote attackers can bypass a $mime_filename extension-blocking protection mechanism, and potentially deliver executable attachments to the mailboxes of end users.

## References
- https://bugs.exim.org/show_bug.cgi?id=3099#c4
- https://git.exim.org/exim.git/commit/1b3209b0577a9327ebb076f3b32b8a159c253f7b
- https://git.exim.org/exim.git/commit/6ce5c70cff8989418e05d01fd2a57703007a6357
- https://github.com/Exim/exim/compare/exim-4.98-RC2...exim-4.98-RC3
- https://www.rfc-editor.org/rfc/rfc2231.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39929.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39929
