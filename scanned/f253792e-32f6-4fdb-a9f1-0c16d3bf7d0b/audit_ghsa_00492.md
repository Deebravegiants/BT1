# [H] Code execution in org.apache.storm:storm-core

## Summary
Severity: High
Advisory: GHSA-p8jx-x2vw-wm33
CVE: CVE-2018-1331
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-p8jx-x2vw-wm33
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-core` — affected >=1.2.0 <1.2.2
- Maven: `org.apache.storm:storm-core` — affected >=0 <1.1.3

## Details
In Apache Storm 0.10.0 through 0.10.2, 1.0.0 through 1.0.6, 1.1.0 through 1.1.2, and 1.2.0 through 1.2.1, an attacker with access to a secure storm cluster in some cases could execute arbitrary code as a different user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1331
- https://github.com/advisories/GHSA-p8jx-x2vw-wm33
- http://storm.apache.org/2018/06/04/storm113-released.html
- http://storm.apache.org/2018/06/04/storm122-released.html
- http://www.openwall.com/lists/oss-security/2018/07/10/4
- http://www.securityfocus.com/bid/104732
- http://www.securitytracker.com/id/1041273
