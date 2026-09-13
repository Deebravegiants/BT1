# [H] In Bouncy Castle JCE Provider ECDSA does not fully validate ASN.1 encoding of signature on verification

## Summary
Severity: High
Advisory: GHSA-qcj7-g2j5-g7r3
CVE: CVE-2016-1000342
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-qcj7-g2j5-g7r3
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.56

## Details
In the Bouncy Castle JCE Provider version 1.55 and earlier ECDSA does not fully validate ASN.1 encoding of signature on verification. It is possible to inject extra elements in the sequence making up the signature and still have it validate, which in some cases may allow the introduction of 'invisible' data into a signed structure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000342
- https://github.com/bcgit/bc-java/commit/843c2e60f67d71faf81d236f448ebbe56c62c647#diff-25c3c78db788365f36839b3f2d3016b9
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/bcgit/bc-java
- https://lists.debian.org/debian-lts-announce/2018/07/msg00009.html
- https://security.netapp.com/advisory/ntap-20181127-0004
- https://usn.ubuntu.com/3727-1
- https://www.oracle.com/security-alerts/cpuoct2020.html
