# [C] Apache HttpComponents Client: TLS hostname verification silently disabled on the async transport (default config, MITM)

## Summary
Severity: Critical
Advisory: CVE-2026-71290
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-71290
Type: osv

## Details
Improper TLS hostname verification vulnerability in Apache HttpComponents Client 5.4 or newer. HostnameVerificationPolicy#BUILTIN setting has no effect when used with the async version of HttpClient. An attacker that can intercept and modify traffic between the client and the server can impersonate the server by presenting a valid certificate for a different domain. 


Please note the classic version of HttpClient is not affected by this vulnerability. 

Affected users are recommended to upgrade to at least version 5.6.4, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/13/6
- https://repo.maven.apache.org/maven2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71290.json
- https://lists.apache.org/thread/bhf7g2zwpom2ohvwjjjlonc93br2s8vq
- https://nvd.nist.gov/vuln/detail/CVE-2026-71290
