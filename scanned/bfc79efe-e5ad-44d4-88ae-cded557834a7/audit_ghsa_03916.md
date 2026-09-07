# [M] Bootstrap Vulnerable to Cross-Site Scripting

## Summary
Severity: Medium
Advisory: GHSA-9v3m-8fp8-mj99
CVE: CVE-2019-8331
CWE: CWE-79
Ecosystem: Maven, NuGet, Packagist, RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-02-22
Source: https://github.com/advisories/GHSA-9v3m-8fp8-mj99
Type: github-advisory

## Affected
- RubyGems: `bootstrap` — affected >=0 <4.3.1
- RubyGems: `bootstrap-sass` — affected >=3.0.0 <3.4.1
- NuGet: `Bootstrap.Less` — affected >=3.0.0 <3.4.1
- NuGet: `bootstrap` — affected >=4.0.0 <4.3.1
- NuGet: `bootstrap` — affected >=3.0.0 <3.4.1
- NuGet: `bootstrap.sass` — affected >=0 <4.3.1
- npm: `bootstrap` — affected >=4.0.0 <4.3.1
- npm: `bootstrap` — affected >=3.0.0 <3.4.1
- npm: `bootstrap-sass` — affected >=3.0.0 <3.4.1
- RubyGems: `twitter-bootstrap-rails` — affected >=0 <5.3.0
- Maven: `org.webjars:bootstrap` — affected >=3.0.0 <3.4.1
- Maven: `org.webjars:bootstrap` — affected >=4.0.0 <4.3.1
- Packagist: `twbs/bootstrap` — affected >=3.0.0 <3.4.1
- Packagist: `twbs/bootstrap` — affected >=4.0.0 <4.3.1

## Details
Versions of `bootstrap` prior to 3.4.1 for 3.x and 4.3.1 for 4.x are vulnerable to Cross-Site Scripting (XSS). The  `data-template` attribute of the tooltip and popover plugins lacks input sanitization and may allow attacker to execute arbitrary JavaScript.


## Recommendation

For `bootstrap` 4.x upgrade to 4.3.1 or later.
For `bootstrap` 3.x upgrade to 3.4.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8331
- https://github.com/twbs/bootstrap/pull/28236
- https://lists.apache.org/thread.html/52e0e6b5df827ee7f1e68f7cc3babe61af3b2160f5d74a85469b7b0e%40%3Cdev.superset.apache.org%3E
- https://lists.apache.org/thread.html/52e0e6b5df827ee7f1e68f7cc3babe61af3b2160f5d74a85469b7b0e@%3Cdev.superset.apache.org%3E
- https://lists.apache.org/thread.html/54df3aeb4239b64b50b356f0ca6f986e3c4ca5b84c515dce077c7854%40%3Cuser.flink.apache.org%3E
- https://lists.apache.org/thread.html/54df3aeb4239b64b50b356f0ca6f986e3c4ca5b84c515dce077c7854@%3Cuser.flink.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442%40%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc%40%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/r3dc0cac8d856bca02bd6997355d7ff83027dcfc82f8646a29b89b714%40%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r3dc0cac8d856bca02bd6997355d7ff83027dcfc82f8646a29b89b714@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://seclists.org/bugtraq/2019/May/18
- https://support.f5.com/csp/article/K24383845
- https://support.f5.com/csp/article/K24383845?utm_source=f5support&amp%3Butm_medium=RSS
- https://support.f5.com/csp/article/K24383845?utm_source=f5support&amp;utm_medium=RSS
- https://web.archive.org/web/20200227083900/http://www.securityfocus.com/bid/107375
- https://www.oracle.com/security-alerts/cpuApr2021.html
