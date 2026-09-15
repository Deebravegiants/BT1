# [M] CVE-2024-43180

## Summary
Severity: Medium
Advisory: CVE-2024-43180
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-43180
Type: osv

## Details
IBM Concert 1.0 does not set the secure attribute on authorization tokens or session cookies. Attackers may be able to get the cookie values by sending a http:// link to a user or by planting this link in a site the user goes to. The cookie will be sent to the insecure link and the attacker can then obtain the cookie value by snooping the traffic.

## References
- https://exchange.xforce.ibmcloud.com/vulnerabilities/351213
- https://www.ibm.com/support/pages/node/7168234
