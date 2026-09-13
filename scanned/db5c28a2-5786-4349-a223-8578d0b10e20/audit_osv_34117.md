# [M] Asterisk remotely exploitable leak of RTP UDP ports and internal resources

## Summary
Severity: Medium
Advisory: CVE-2025-54995
Aliases: GHSA-557q-795j-wfx2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2025-54995
Type: osv

## Details
Asterisk is an open source private branch exchange and telephony toolkit. Prior to versions 18.26.4 and 18.9-cert17, RTP UDP ports and internal resources can leak due to a lack of session termination. This could result in leaks and resource exhaustion. This issue has been patched in versions 18.26.4 and 18.9-cert17.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00006.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54995.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-557q-795j-wfx2
- https://nvd.nist.gov/vuln/detail/CVE-2025-54995
- https://github.com/asterisk/asterisk/commit/0278f5bde14565c6838a6ec39bc21aee0cde56a9
- https://github.com/asterisk/asterisk/commit/eafcd7a451dcd007dddf324ac37dd55a4808338d
- https://github.com/asterisk/asterisk/pull/1405
- https://github.com/asterisk/asterisk/pull/1406
