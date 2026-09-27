# [M] Roundcube Local/Private URL Fetch Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-9818
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-9818
Type: osv

## Details
Roundcube's HTML sanitization path for message rendering allows loopback, localhost, RFC1918, link-local, and ULA URLs even when remote content loading is disabled. A remote attacker can send an HTML email that causes the victim's browser to issue requests to local or private-network services simply by opening the message preview.

## References
- https://github.com/roundcube/roundcubemail/
- https://advisories.orangecyberdefense.com/advisories/163
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9818.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9818
- https://github.com/roundcube/roundcubemail/commit/7b52353653a67e6073b97d70eb94047132b78556
- https://github.com/roundcube/roundcubemail/commit/faf867432f51ebbe100382a70a9e3c042415ee1b
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.16
- https://github.com/roundcube/roundcubemail/releases/tag/1.7.1
