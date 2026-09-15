# [H] SecureDrop Client has path injection in read_gzip_header_filename()

## Summary
Severity: High
Advisory: CVE-2026-35465
Aliases: GHSA-2jrc-x8fq-prvc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-35465
Type: osv

## Details
SecureDrop Client is a desktop app for journalists to securely communicate with sources and handle submissions on the SecureDrop Workstation. In versions 0.17.4 and below, a compromised SecureDrop Server can achieve code execution on the Client's virtual machine (sd-app) by exploiting improper filename validation in gzip archive extraction, which permits absolute paths and enables overwriting critical files like the SQLite database. Exploitation requires prior compromise of the dedicated SecureDrop Server, which itself is hardened and only accessible via Tor hidden services. Despite the high attack complexity, the vulnerability is rated High severity due to its significant impact on confidentiality, integrity, and availability of decrypted source submissions. This issue is similar to CVE-2025-24888 but occurs through a different code path, and a more robust fix has been implemented in the replacement SecureDrop Inbox codebase. The issue has been fixed in version 0.17.5.

## References
- https://github.com/freedomofpress/securedrop-client/blob/8dc8bb6e307b13876d67f72d8a071202e2f39ab5/changelog.md?plain=1#L8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35465.json
- https://github.com/freedomofpress/securedrop-client/security/advisories/GHSA-2jrc-x8fq-prvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-35465
- https://github.com/freedomofpress/securedrop-client/commit/e518adaf897e7838467ccf9e1f28152ae6fe3655
