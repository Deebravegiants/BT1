# [H] Apache HttpComponents Core: HPackDecoder Unlimited Header List Size Before SETTINGS ACK

## Summary
Severity: High
Advisory: GHSA-v3jc-474w-2wm6
CVE: CVE-2026-54428
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-v3jc-474w-2wm6
Type: github-advisory

## Affected
- Maven: `org.apache.httpcomponents.core5:httpcore5-h2` — affected >=0 <5.4.3
- Maven: `org.apache.httpcomponents.core5:httpcore5-h2` — affected >=5.5-alpha1 <5.5-beta2

## Details
Allocation of resources without limits or throttling in the HTTP/2 HPACK decoder in Apache HttpComponents Core (5.4.2 and earlier, 5.5-beta1 and earlier) allows an remote attacker to cause a denial of service through memory exhaustion by sending oversized compressed header blocks before the HTTP/2 SETTINGS acknowledgement causes the configured header list size limit to be applied.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-54428
- https://github.com/apache/httpcomponents-core/commit/1ea1239bbbe3442a8382a87279c0a8119a7e358e
- https://github.com/apache/httpcomponents-core/commit/cc30ee058a7b10cbf4ad3dd6270ab6d1f6a74c49
- https://github.com/apache/httpcomponents-core
- https://lists.apache.org/thread/5zjp8vczvxq19pw2rvhs21q446bhl0sd
- http://www.openwall.com/lists/oss-security/2026/07/01/3
