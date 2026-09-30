# [M] ImapEngine affected by command injection via the ID command parameters

## Summary
Severity: Medium
Advisory: GHSA-rfq9-4wcm-64gh
CVE: CVE-2026-2469
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-02-14
Source: https://github.com/advisories/GHSA-rfq9-4wcm-64gh
Type: github-advisory

## Affected
- Packagist: `directorytree/imapengine` — affected >=0 <1.22.3

## Details
Versions of the package `directorytree/imapengine` before 1.22.3 are vulnerable to Improper Neutralization of Special Elements in Output Used by a Downstream Component ('Injection') via the id() function in ImapConnection.php due to improperly escaping user input before including it in IMAP ID commands. This allows attackers to read or delete victim's emails, terminate the victim's session or execute any valid IMAP command on victim's mailbox by including quote characters `"` or CRLF sequences `\r\n` in the input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2469
- https://github.com/DirectoryTree/ImapEngine/pull/150
- https://github.com/DirectoryTree/ImapEngine/commit/87fca56affd9527e6907a705e6d600c5174d9a5a
- https://gist.github.com/wanamirulhakim/74b41589cdea3c07c3375e5946960778
- https://github.com/DirectoryTree/ImapEngine
- https://security.snyk.io/vuln/SNYK-PHP-DIRECTORYTREEIMAPENGINE-15274300
