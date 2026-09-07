# [H] Improper Authorization in org.cometd.oort

## Summary
Severity: High
Advisory: GHSA-rjmq-6v55-4rjv
CVE: CVE-2022-24721
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-15
Source: https://github.com/advisories/GHSA-rjmq-6v55-4rjv
Type: github-advisory

## Affected
- Maven: `org.cometd.java:cometd-java-oort` — affected >=0 <5.0.11
- Maven: `org.cometd.java:cometd-java-oort` — affected >=6.0.0 <6.0.6
- Maven: `org.cometd.java:cometd-java-oort` — affected >=7.0.0 <7.0.6

## Details
### Impact
Internal usage of Oort and Seti channels is improperly authorized, so any remote user could subscribe and publish to those channels.
By subscribing to those channels, a remote user may be able to watch cluster-internal traffic that contains other user's (possibly sensitive) data.
By publishing to those channels, a remote user may be able to create/modify/delete other user's data and modify the cluster structure.
The issue impacts any version up to 5.0.10, 6.0.5 and 7.0.5.

### Patches
The issue has been fixed in 5.0.11, 6.0.6 and 7.0.6.

### Workarounds
The workaround is to install a custom `SecurityPolicy` that forbids subscription and publishing to remote, non-Oort, sessions on Oort and Seti channels.
This workaround could be implemented in any affected version.

### References
cometd/cometd#1146

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@webtide.com](mailto:security@webtide.com)

### Credits
https://www.redteam-pentesting.de/

## References
- https://github.com/cometd/cometd/security/advisories/GHSA-rjmq-6v55-4rjv
- https://nvd.nist.gov/vuln/detail/CVE-2022-24721
- https://github.com/cometd/cometd/issues/1146
- https://github.com/cometd/cometd/commit/bb445a143fbf320f17c62e340455cd74acfb5929
- https://github.com/cometd/cometd
