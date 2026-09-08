# [H] Missing Encryption of Sensitive Data in Apache Guacamole

## Summary
Severity: High
Advisory: GHSA-wr7r-vg3c-54r5
CVE: CVE-2018-1340
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wr7r-vg3c-54r5
Type: github-advisory

## Affected
- Maven: `org.apache.guacamole:guacamole-common` — affected >=0 <1.0.0

## Details
Prior to 1.0.0, Apache Guacamole used a cookie for client-side storage of the user's session token. This cookie lacked the "secure" flag, which could allow an attacker eavesdropping on the network to intercept the user's session token if unencrypted HTTP requests are made to the same domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1340
- https://lists.apache.org/thread.html/af1632e13dd9acf7537546660cae9143cbb10fdd2f9bb0832a690979@%3Cannounce.guacamole.apache.org%3E
- http://www.securityfocus.com/bid/106768
