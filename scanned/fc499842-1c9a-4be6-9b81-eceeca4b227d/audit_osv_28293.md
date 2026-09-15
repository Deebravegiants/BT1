# [M] CVE-2024-31033

## Summary
Severity: Medium
Advisory: CVE-2024-31033
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-04-01
Source: https://osv.dev/vulnerability/CVE-2024-31033
Type: osv

## Details
JJWT (aka Java JWT) through 0.12.5 ignores certain characters and thus a user might falsely conclude that they have a strong key. The impacted code is the setSigningKey() method within the DefaultJwtParser class and the signWith() method within the DefaultJwtBuilder class. NOTE: the vendor disputes this because the "ignores" behavior cannot occur (in any version) unless there is a user error in how JJWT is used, and because the version that was actually tested must have been more than six years out of date.

## References
- https://www.viralpatel.net/java-create-validate-jwt-token/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31033.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31033
- https://github.com/jwtk/jjwt/issues/930#issuecomment-2032699358
- https://github.com/2308652512/JJWT_BUG
- https://github.com/jwtk/jjwt
