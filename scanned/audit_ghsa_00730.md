# [M] Log Forging in generator-jhipster-kotlin

## Summary
Severity: Medium
Advisory: GHSA-pfxf-wh96-fvjc
CVE: CVE-2020-4072
CWE: CWE-117
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-06-25
Source: https://github.com/advisories/GHSA-pfxf-wh96-fvjc
Type: github-advisory

## Affected
- npm: `generator-jhipster-kotlin` — affected >=1.6.0 <1.7.0

## Details
### Impact

We log the mail for invalid password reset attempts. 
As the email is provided by a user and the api is public this can be used by an attacker to forge log entries.
This is vulnerable to https://cwe.mitre.org/data/definitions/117.html

This problem affects only application generated with jwt or session authentication. Applications using oauth are not vulnerable.

### Patches

version 1.7.0.

### Workarounds

In `AccountResource.kt` you should change the line

```kotlin
 log.warn("Password reset requested for non existing mail '$mail'");
```

to 

```kotlin
 log.warn("Password reset requested for non existing mail");
```

### References

* https://cwe.mitre.org/data/definitions/117.html
* https://owasp.org/www-community/attacks/Log_Injection
* https://www.baeldung.com/jvm-log-forging

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [jhipster kotlin](https://github.com/jhipster/jhipster-kotlin)

## References
- https://github.com/jhipster/jhipster-kotlin/security/advisories/GHSA-pfxf-wh96-fvjc
- https://nvd.nist.gov/vuln/detail/CVE-2020-4072
- https://github.com/jhipster/jhipster-kotlin/commit/426ccab85e7e0da562643200637b99b6a2a99449
- https://owasp.org/www-community/attacks/Log_Injection
- https://www.baeldung.com/jvm-log-forging
