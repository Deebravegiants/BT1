# [H] Incorrect management of session invalidation vulnerability in Graylog Web Interface

## Summary
Severity: High
Advisory: CVE-2026-1435
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-1435
Type: osv

## Details
Not properly invalidated session vulnerability in Graylog Web Interface, version 2.2.3, due to incorrect management of session invalidation after new logins. The application generates a new 'sessionId' each time a user authenticates, but does not invalidate previously issued session identifiers, which remain valid even after multiple consecutive logins by the same user. As a result, a stolen or leaked 'sessionId' can continue to be used to authenticate valid requests. Exploiting this vulnerability would allow an attacker with access to the web service/API network (port 9000 or HTTP/S endpoint of the server) to reuse an old session token to gain unauthorized access to the application, interact with the API/web, and compromise the integrity of the affected account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1435.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-1435
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-graylog
