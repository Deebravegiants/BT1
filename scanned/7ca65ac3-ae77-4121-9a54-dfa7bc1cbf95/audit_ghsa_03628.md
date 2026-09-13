# [M] Low severity vulnerability that affects com.linecorp.armeria:armeria

## Summary
Severity: Medium
Advisory: GHSA-24r8-fm9r-cpj2
CVE: CVE-2019-16771
CWE: CWE-113
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2019-12-05
Source: https://github.com/advisories/GHSA-24r8-fm9r-cpj2
Type: github-advisory

## Affected
- Maven: `com.linecorp.armeria:armeria` — affected >=0.50.0 <0.97.0

## Details
## Multiple timing attack vulnerabilities leading to the recovery of secrets based on the use of non-constant time compare function

### Impact

String comparison method in multiple authentication validation in Armeria were known to be vulnerable to timing attacks. This vulnerability is caused by the insecure implementation of `equals` method from `java.lang.String`. While this attack is not practically possible, an attacker still has a potential to attack if the victim's server validates user by using `equals` method.

We would like to thank @chrsow for pointing out the issue.

## Potentially vulnerable codes

https://github.com/line/armeria/blob/f0d870fde1088114070be31b67f7df0a21e835c6/core/src/main/java/com/linecorp/armeria/server/auth/OAuth2Token.java#L54
https://github.com/line/armeria/blob/f0d870fde1088114070be31b67f7df0a21e835c6/core/src/main/java/com/linecorp/armeria/server/auth/BasicToken.java#L64

### Patches

There are two options to patch this issue.

1. Remove `equals` method; it has been exclusively used for test cases and was never used in any OSS projects that are using Armeria. (But it is worth noting that there are possibilities of closed projects authenticating users by utilizing `equals` method)

2. Use `MessageDigest.isEqual` to compare the credential instead.

### Workarounds

1. Update to the latest version (TBD)

2-1. Users can prevent these vulnerabilities by modifying and implementing timing attack preventions by themselves.

2-2. Precisely speaking, it is possible to compare credentials by securely comparing them after calling methods to directly return the input (namely `Object. accessToken()`, `Object.username()` and `Object.password()`).

### References
- https://cwe.mitre.org/data/definitions/208.html
- https://security.stackexchange.com/questions/111040/should-i-worry-about-remote-timing-attacks-on-string-comparison

### Side Note

Since it is a theoretical attack, there is no PoC available from neither the vendor nor the security team.

## References
- https://github.com/line/armeria/security/advisories/GHSA-24r8-fm9r-cpj2
- https://github.com/line/armeria/security/advisories/GHSA-35fr-h7jr-hh86
- https://nvd.nist.gov/vuln/detail/CVE-2019-16771
- https://github.com/line/armeria/commit/b597f7a865a527a84ee3d6937075cfbb4470ed20
- https://github.com/advisories/GHSA-24r8-fm9r-cpj2
