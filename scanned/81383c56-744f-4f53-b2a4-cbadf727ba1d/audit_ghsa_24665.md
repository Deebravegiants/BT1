# [M] Ignite Realtime Openfire Allows Users to Change Passwords of Arbitrary Accounts

## Summary
Severity: Medium
Advisory: GHSA-r62w-x9pp-jrqp
CVE: CVE-2009-1595
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-r62w-x9pp-jrqp
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:parent` — affected >=0 <3.6.4

## Details
The `jabber:iq:auth` implementation in `IQAuthHandler.java` in Ignite Realtime Openfire before 3.6.4 allows remote authenticated users to change the passwords of arbitrary accounts via a modified username element in a `passwd_change` action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-1595
- https://github.com/igniterealtime/Openfire/commit/97e1f08cf72e430f5cca5ba94cd20703dadb5ce5
- https://download.igniterealtime.org/openfire/docs/latest/changelog.html#3.6.4
- https://exchange.xforce.ibmcloud.com/vulnerabilities/50292
- https://github.com/igniterealtime/Openfire
- https://web.archive.org/web/20090518061336/http://www.igniterealtime.org/issues/browse/JM-1531
- https://web.archive.org/web/20140901211944/http://www.securityfocus.com/bid/34804
- http://www.igniterealtime.org/community/message/190280
