# [C] CVE-2025-11165

## Summary
Severity: Critical
Advisory: CVE-2025-11165
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2025-11165
Type: osv

## Details
A sandbox escape vulnerability exists in dotCMS’s Velocity scripting engine (VTools) that allows authenticated users with scripting privileges to bypass class and package restrictions enforced by SecureUberspectorImpl.

By dynamically modifying the Velocity engine’s runtime configuration and reinitializing its Uberspect, a malicious actor can remove the introspector.restrict.classes and introspector.restrict.packages protections.

Once these restrictions are cleared, the attacker can access arbitrary Java classes, including java.lang.Runtime, and execute arbitrary system commands under the privileges of the application process (e.g. dotCMS or Tomcat user).

## References
- https://dev.dotcms.com/docs/known-security-issues?issueNumber=SI-74
- https://www.dotcms.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11165.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11165
