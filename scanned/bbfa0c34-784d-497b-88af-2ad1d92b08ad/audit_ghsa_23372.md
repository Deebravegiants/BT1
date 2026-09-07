# [M] Smack allows the bypass of TLS protections

## Summary
Severity: Medium
Advisory: GHSA-66pq-hqv5-228g
CVE: CVE-2016-10027
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-66pq-hqv5-228g
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.smack:smack-core` — affected >=0 <4.1.9

## Details
Race condition in the XMPP library in Smack before 4.1.9, when the SecurityMode.required TLS setting has been set, allows man-in-the-middle attackers to bypass TLS protections and trigger use of cleartext for client authentication by stripping the "starttls" feature from a server response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10027
- https://github.com/igniterealtime/Smack/commit/059ee99ba0d5ff7758829acf5a9aeede09ec820b
- https://github.com/igniterealtime/Smack/commit/a9d5cd4a611f47123f9561bc5a81a4555fe7cb04
- https://community.igniterealtime.org/blogs/ignite/2016/11/22/smack-security-advisory-2016-11-22
- https://github.com/igniterealtime/Smack
- https://issues.igniterealtime.org/projects/SMACK/issues/SMACK-739
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J4WXAZ4JVJXHMEDDXJVWJHPVBF5QCTZF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J4WXAZ4JVJXHMEDDXJVWJHPVBF5QCTZF
- http://www.openwall.com/lists/oss-security/2016/12/22/12
