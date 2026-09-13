# [H] CVE-2014-9773

## Summary
Severity: High
Advisory: CVE-2014-9773
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2014-9773
Type: osv

## Details
modules/chanserv/flags.c in Atheme before 7.2.7 allows remote attackers to modify the Anope FLAGS behavior by registering and dropping the (1) LIST, (2) CLEAR, or (3) MODIFY keyword nicks.

## References
- https://github.com/atheme/atheme/commit/c597156adc60a45b5f827793cd420945f47bc03b
- https://github.com/atheme/atheme/issues/397
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00061.html
- http://www.openwall.com/lists/oss-security/2016/05/02/2
- http://www.openwall.com/lists/oss-security/2016/05/03/1
