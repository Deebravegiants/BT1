# [H] Ignite Realtime Openfire privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-5xvc-rwv8-86p7
CVE: CVE-2024-25420
CWE: CWE-273, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-26
Source: https://github.com/advisories/GHSA-5xvc-rwv8-86p7
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:xmppserver` — affected >=0 <4.8.1

## Details
An issue in Ignite Realtime Openfire v.4.8.0 and before allows a remote attacker to escalate privileges via the admin.authorizedJIDs system property component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25420
- https://github.com/igniterealtime/Openfire/pull/2411
- https://github.com/igniterealtime/Openfire/commit/5c022bfa82d71d1710381ab395b100cdbcb8f310
- https://github.com/igniterealtime/Openfire
- https://github.com/igniterealtime/Openfire/blob/main/xmppserver/src/main/java/org/jivesoftware/openfire/admin/AdminManager.java
- https://github.com/igniterealtime/Openfire/releases/tag/v4.8.1
- https://igniterealtime.atlassian.net/browse/OF-2758
- https://www.hackthebox.com/blog/openfire-cves-explained-CVE-2024-25420-CVE-2024-25421
- https://www.igniterealtime.org/projects/openfire
