# [H] The Bouncy Castle JCE Provider carry a propagation bug

## Summary
Severity: High
Advisory: GHSA-r97x-3g8f-gx3m
CVE: CVE-2016-1000340
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-r97x-3g8f-gx3m
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.51 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=1.51 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=1.51 <1.56

## Details
In the Bouncy Castle JCE Provider versions 1.51 to 1.55, a carry propagation bug was introduced in the implementation of squaring for several raw math classes have been fixed (org.bouncycastle.math.raw.Nat???). These classes are used by our custom elliptic curve implementations (org.bouncycastle.math.ec.custom.**), so there was the possibility of rare (in general usage) spurious calculations for elliptic curve scalar multiplications. Such errors would have been detected with high probability by the output validation for our scalar multipliers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000340
- https://github.com/bcgit/bc-java/commit/790642084c4e0cadd47352054f868cc8397e2c00#diff-e5934feac8203ca0104ab291a3560a31
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/advisories/GHSA-r97x-3g8f-gx3m
- https://github.com/bcgit/bc-java
- https://security.netapp.com/advisory/ntap-20181127-0004
- https://www.oracle.com/security-alerts/cpuoct2020.html
