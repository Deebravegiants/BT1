# [M] CVE-2021-37629

## Summary
Severity: Medium
Advisory: CVE-2021-37629
Aliases: GHSA-gvvr-h36p-8mjx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-37629
Type: osv

## Details
Nextcloud Richdocuments is an open source collaborative office suite. In affected versions there is a lack of rate limiting on the Richdocuments OCS endpoint. This may have allowed an attacker to enumerate potentially valid share tokens. It is recommended that the Nextcloud Richdocuments app is upgraded to either 3.8.4 or 4.2.1 to resolve. For users unable to upgrade it is recommended that the Richdocuments application be disabled.

## References
- https://github.com/nextcloud/richdocuments/pull/1663
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-gvvr-h36p-8mjx
- https://hackerone.com/reports/1258750
