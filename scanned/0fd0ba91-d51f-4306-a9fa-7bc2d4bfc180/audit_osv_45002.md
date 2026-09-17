# [M] CVE-2026-9561

## Summary
Severity: Medium
Advisory: CVE-2026-9561
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-9561
Type: osv

## Details
Eclipse Kura versions prior to 5.6.2 trust the client-supplied X-Forwarded-For HTTP header as the authoritative source of the client IP address in audit log entries. The org.eclipse.kura.web2 (Web Console) and org.eclipse.kura.rest.provider (REST API) components use this header as the primary IP source when initializing audit context, and org.eclipse.kura.jetty.customizer unconditionally installs Jetty's ForwardedRequestCustomizer on all HTTP/HTTPS connectors, causing HttpServletRequest.getRemoteAddr() to reflect the attacker-controlled header value. An unauthenticated remote attacker can exploit this vulnerability to bypass IP-based brute-force protections — such as fail2ban — by spoofing the logged IP address to a non-routable value, allowing a brute-force attack to proceed undetected, or to cause a denial of service against a third party by injecting a victim's IP address and triggering a ban on that address.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/117
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9561.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9561
- https://github.com/eclipse-kura/kura
