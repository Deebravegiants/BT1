# [M] Expired Ephemeral Messages not reliably removed in wire-webapp

## Summary
Severity: Medium
Advisory: CVE-2022-23605
Aliases: GHSA-2w3m-ppfg-hg62
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2022-23605
Type: osv

## Details
Wire webapp is a web client for the wire messaging protocol. In versions prior to 2022-01-27-production.0 expired ephemeral messages were not reliably removed from local chat history of Wire Webapp. In versions before 2022-01-27-production.0 ephemeral messages and assets might still be accessible through the local search functionality. Any attempt to view one of these message in the chat view will then trigger the deletion. This issue only affects locally stored messages. On premise instances of wire-webapp need to be updated to 2022-01-27-production.0, so that their users are no longer affected. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23605.json
- https://github.com/wireapp/wire-webapp/security/advisories/GHSA-2w3m-ppfg-hg62
- https://nvd.nist.gov/vuln/detail/CVE-2022-23605
- https://github.com/wireapp/wire-webapp/commit/42c9a1edddbdd5d4d8f9a196a98f6fc19bb21741
