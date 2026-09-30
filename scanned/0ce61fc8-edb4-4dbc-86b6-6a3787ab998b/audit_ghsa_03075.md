# [C] Improper Authentication in Apache Traffic Control

## Summary
Severity: Critical
Advisory: GHSA-3f8r-4qwm-r7jf
CVE: CVE-2019-12405
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-3f8r-4qwm-r7jf
Type: github-advisory

## Affected
- Go: `github.com/apache/trafficcontrol` — affected >=3.0.0 <3.0.2-RC1

## Details
Improper authentication is possible in Apache Traffic Control versions 3.0.0 and 3.0.1 if LDAP is enabled for login in the Traffic Ops API component. Given a username for a user that can be authenticated via LDAP, it is possible to improperly authenticate as that user without that user's correct password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12405
- https://github.com/apache/trafficcontrol/commit/f780aff77a52d52a37b4d1cc3e8e801c0b557356
- https://github.com/apache/trafficcontrol
- https://lists.apache.org/thread.html/e128e9d382f3b0d074e2b597ac58e1d92139394509d81ddbc9e3700e@%3Cusers.trafficcontrol.apache.org%3E
- https://lists.apache.org/thread.html/r3c675031ac220b5eae64a9c84a03ee60045c6045738607dca4a96cb8@%3Ccommits.trafficcontrol.apache.org%3E
- https://lists.apache.org/thread.html/rc8bfd7d4f71d61e9193efcd4699eccbab3c202ec1d75ed9d502f08bf@%3Ccommits.trafficcontrol.apache.org%3E
- https://support.f5.com/csp/article/K84141859
- https://support.f5.com/csp/article/K84141859?utm_source=f5support&amp;utm_medium=RSS
