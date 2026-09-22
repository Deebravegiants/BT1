# [M] OneUptime before 12.0.7 Server-Side Request Forgery via IPv4-Mapped IPv6 Webhook URL

## Summary
Severity: Medium
Advisory: CVE-2026-80350
Aliases: GHSA-9g3w-r349-3vvw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80350
Type: osv

## Details
OneUptime's webhook target check rejects private and loopback addresses given in IPv4 form and a small set of IPv6 forms, but has no case for the IPv4-mapped IPv6 range. The webhook delivery path calls SSRFProtection.validateWebhookTargetIsSafe, and the host-literal screening inside Common/Server/Utils/SSRFProtection.ts, performed by isBlockedHostnameLiteral, rejects private and loopback IPv4 ranges and tests an IPv6 value against the unspecified address, the loopback, the link-local prefix and the unique-local prefixes. A value such as [::ffff:127.0.0.1] matches none of them. The value is also recognised as an address literal rather than a name, so the path that re-checks addresses obtained from resolution is not taken. The HTTP client treats the mapped form as the embedded IPv4 address and connects to it, so an authenticated project member who can configure a webhook can direct the server at loopback services, private network ranges and link-local metadata endpoints, and the response is recorded where the webhook result can be read. Version 12.0.7 adds handling for the mapped range.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80350.json
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-9g3w-r349-3vvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-80350
- https://www.vulncheck.com/advisories/oneuptime-before-12.0.7-server-side-request-forgery-via-ipv4-mapped-ipv6-webhook-url
- https://github.com/OneUptime/oneuptime/issues/2578
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/blob/12.0.6/Common/Server/Utils/SSRFProtection.ts
