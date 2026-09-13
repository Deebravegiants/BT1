# [M] TheHive 4.1.24 Broken Object Level Authorization via Attachment Download Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-63099
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-63099
Type: osv

## Details
TheHive through 4.1.24 contains a broken object-level authorization vulnerability in the attachment download endpoints that allows any authenticated user to access attachments belonging to other organizations by supplying a content-hash identifier. Attackers can exploit the missing organization-scoped authorization check in AttachmentSrv.visible, which is implemented as a pass-through traversal, to download arbitrary attachments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63099.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63099
- https://www.vulncheck.com/advisories/thehive-broken-object-level-authorization-via-attachment-download-endpoints
- https://github.com/TheHive-Project/TheHive
- https://github.com/geo-chen/oss/blob/main/TheHive.md#finding-2-cross-organisation-attachment-disclosure-via-unauthorized-datastore-endpoint-missing-object-level-authorization
