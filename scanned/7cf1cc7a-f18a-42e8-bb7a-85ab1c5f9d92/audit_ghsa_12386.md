# [M] Password Change Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-88j4-pcx8-q4q3
CVE: CVE-2023-49804
CWE: CWE-384
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-12
Source: https://github.com/advisories/GHSA-88j4-pcx8-q4q3
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected >=0 <1.23.9

## Details
## Overview:

A moderate security vulnerability has been identified in Uptime Kuma platform that poses a significant threat to the confidentiality and integrity of user accounts.  
When a user changes their login password in Uptime Kuma, a previously logged-in user retains access without being logged out.
This behaviour persists consistently, even after system restarts or browser restarts.
This vulnerability allows unauthorized access to user accounts, compromising the security of sensitive information.

The same vulnerability was partially fixed in https://github.com/louislam/uptime-kuma/security/advisories/GHSA-g9v2-wqcj-j99g but logging existing users out of their accounts was forgotten.

## Impact:

The impact of this vulnerability is moderate, as it enables attackers or unauthorized individuals to maintain access to user accounts even after the account password has been changed. This can lead to unauthorized data access, manipulation, or compromise of user accounts, posing a threat to the integrity and confidentiality of Uptime Kuma.
A better impact-analysis is included in https://github.com/louislam/uptime-kuma/security/advisories/GHSA-g9v2-wqcj-j99g

## PoC

- Change the password for a user account
- Access the platform using the previously logged-in account without logging out
- Note that access (read-write) remains despite the password change 
- Expected behaviour:  
   After changing the password for a user account, all previously logged-in sessions should be invalidated, requiring users to log in again with the updated credentials.
- Actual behaviour:  
  The system retains sessions and never logs out users unless explicitly done by clicking logout.

## Remediation:

To mitigate the risks associated with this vulnerability, we made the server emit a `refresh` event (clients handle this by reloading) and then disconnecting all clients except the one initiating the password change.

It is recommended to Update Uptime Kuma to `>= 1.23.9`. 

## Timeline:

|Date|Event|
|--|--|
|2023-12-07 14:35 UTC| @manoonabbasi discovered and posts this information as a `bug`-report in issue #4188 [^1] into our **public issue tracker**, which is [**against our security policy**](https://github.com/louislam/uptime-kuma/security/policy) |
| 2023-12-07 16:50 UTC | The Uptime Kuma team deleted the post in our issue tracker |
| 2023-12-10 18:10 UTC | Uptime Kuma team released patch and this Advisory |

[^1]: deleted to prevent the spread of this vulnerability without there being a fix available

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-88j4-pcx8-q4q3
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-g9v2-wqcj-j99g
- https://nvd.nist.gov/vuln/detail/CVE-2023-49804
- https://github.com/louislam/uptime-kuma/commit/482049c72b3a650c7bc5c26c2f4d57a21c0e0aa0
- https://github.com/louislam/uptime-kuma
