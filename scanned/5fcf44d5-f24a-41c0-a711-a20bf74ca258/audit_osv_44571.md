# [H] WWBN AVideo Authentication Bypass via User-Agent Header

## Summary
Severity: High
Advisory: CVE-2026-84479
Aliases: GHSA-m9m3-gwh2-337c
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84479
Type: osv

## Details
WWBN AVideo (current e01e41ecc and earlier) makes three login-time security controls depend solely on the client-supplied User-Agent header. The isAVideoEncoder()/isAVideoMobileApp() checks match HTTP_USER_AGENT against a hardcoded literal ("AVideoEncoder"/"AVideoMobileApp") with no IP check or shared secret. An attacker who submits valid credentials and sets User-Agent: AVideoEncoder bypasses two-factor authentication, skips brute-force captcha escalation, and avoids being recorded in the login/device audit history. No patch is available at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84479.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-m9m3-gwh2-337c
- https://nvd.nist.gov/vuln/detail/CVE-2026-84479
- https://www.vulncheck.com/advisories/wwbn-avideo-authentication-bypass-via-user-agent-header
