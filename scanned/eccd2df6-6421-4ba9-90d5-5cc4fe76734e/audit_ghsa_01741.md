# [M] Prototype Pollution in minimist

## Summary
Severity: Medium
Advisory: GHSA-vh95-rmgr-6w4m
CVE: CVE-2020-7598
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-04-03
Source: https://github.com/advisories/GHSA-vh95-rmgr-6w4m
Type: github-advisory

## Affected
- npm: `minimist` — affected >=0 <0.2.1
- npm: `minimist` — affected >=1.0.0 <1.2.3

## Details
Affected versions of `minimist` are vulnerable to prototype pollution. Arguments are not properly sanitized, allowing an attacker to modify the prototype of `Object`, causing the addition or modification of an existing property that will exist on all objects.  
Parsing the argument `--__proto__.y=Polluted` adds a `y` property with value `Polluted` to all objects. The argument `--__proto__=Polluted` raises and uncaught error and crashes the application.  
This is exploitable if attackers have control over the arguments being passed to `minimist`.


## Recommendation

Upgrade to versions 0.2.1, 1.2.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7598
- https://github.com/minimistjs/minimist/commit/10bd4cdf49d9686d48214be9d579a9cdfda37c68
- https://github.com/minimistjs/minimist/commit/38a4d1caead72ef99e824bb420a2528eec03d9ab
- https://github.com/minimistjs/minimist/commit/4cf1354839cb972e38496d35e12f806eea92c11f#diff-a1e0ee62c91705696ddb71aa30ad4f95
- https://github.com/minimistjs/minimist/commit/63e7ed05aa4b1889ec2f3b196426db4500cbda94
- https://github.com/substack/minimist
- https://snyk.io/vuln/SNYK-JS-MINIMIST-559764
- https://www.npmjs.com/advisories/1179
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00024.html
