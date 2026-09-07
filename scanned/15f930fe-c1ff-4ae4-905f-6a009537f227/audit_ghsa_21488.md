# [H] Failing DTLS handshakes may cause throttling to block processing of records

## Summary
Severity: High
Advisory: GHSA-p72g-cgh9-ghjg
CVE: CVE-2022-39368
CWE: CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2022-11-09
Source: https://github.com/advisories/GHSA-p72g-cgh9-ghjg
Type: github-advisory

## Affected
- Maven: `org.eclipse.californium:scandium` — affected >=3.0.0 <3.7.0
- Maven: `org.eclipse.californium:scandium` — affected >=2.7.0 <2.7.4

## Details
### Impact

Failing handshakes didn't cleanup counters for throttling. In consequence the threshold may get reached and will not be released again. The results in permanently dropping records. The issues was reported for certificate based handshakes, but it can't be excluded, that this happens also for PSK based handshakes. It generally affects client and server as well.

### Patches

main: commit 726bac57659410da463dcf404b3e79a7312ac0b9 
2.7.x: commit 5648a0c27c2c2667c98419254557a14bac2b1f3f

Users are requested to update to 3.7.0. If Californium 2 support is required, users are requested to update to 2.7.4. 

### Workarounds
none.

## References
- https://github.com/eclipse-californium/californium/security/advisories/GHSA-p72g-cgh9-ghjg
- https://nvd.nist.gov/vuln/detail/CVE-2022-39368
- https://github.com/eclipse-californium/californium/issues/2065
- https://github.com/eclipse-californium/californium/commit/5648a0c27c2c2667c98419254557a14bac2b1f3f
- https://github.com/eclipse-californium/californium/commit/726bac57659410da463dcf404b3e79a7312ac0b9
- https://cwe.mitre.org/data/definitions/452.html
- https://github.com/eclipse-californium/californium
