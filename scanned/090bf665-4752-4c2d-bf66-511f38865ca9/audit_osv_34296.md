# [H] Asterisk can crash from a specifically malformed Authorization header in an incoming SIP request

## Summary
Severity: High
Advisory: CVE-2025-57767
Aliases: GHSA-64qc-9x89-rx5j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2025-57767
Type: osv

## Details
Asterisk is an open source private branch exchange and telephony toolkit. Prior to versions 20.15.2, 21.10.2, and 22.5.2, if a SIP request is received with an Authorization header that contains a realm that wasn't in a previous 401 response's WWW-Authenticate header, or an Authorization header with an incorrect realm was received without a previous 401 response being sent, the get_authorization_header() function in res_pjsip_authenticator_digest will return a NULL. This wasn't being checked before attempting to get the digest algorithm from the header which causes a SEGV. This issue has been patched in versions 20.15.2, 21.10.2, and 22.5.2. There are no workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57767.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-64qc-9x89-rx5j
- https://nvd.nist.gov/vuln/detail/CVE-2025-57767
- https://github.com/asterisk/asterisk/commit/02993717b08f899d4aca9888062f35dfb198584f
- https://github.com/asterisk/asterisk/pull/1407
