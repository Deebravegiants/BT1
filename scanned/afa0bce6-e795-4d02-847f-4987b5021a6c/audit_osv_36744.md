# [M] WeKan < 8.19 Attachment Upload Object Relationship Validation Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-25561
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-07
Source: https://osv.dev/vulnerability/CVE-2026-25561
Type: osv

## Details
WeKan versions prior to 8.19 contain an authorization weakness in the attachment upload API. The API does not fully validate that provided identifiers (such as boardId, cardId, swimlaneId, and listId) are consistent and refer to a coherent card/board relationship, enabling attempts to upload attachments with mismatched object relationships.

## References
- https://wekan.fi/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25561.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25561
- https://www.vulncheck.com/advisories/wekan-attachment-upload-object-relationship-validation-bypass
- https://github.com/wekan/wekan/commit/1d16955b6d4f0a0282e89c2c1b0415c7597019b8
- https://github.com/wekan/wekan
