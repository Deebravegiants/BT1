# [M] Moderate severity vulnerability that affects org.bouncycastle:bcprov-jdk14 and org.bouncycastle:bcprov-jdk15

## Summary
Severity: Medium
Advisory: GHSA-9gp4-qrff-c648
CVE: CVE-2016-1000345
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-9gp4-qrff-c648
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.56

## Details
In the Bouncy Castle JCE Provider version 1.55 and earlier the DHIES/ECIES CBC mode vulnerable to padding oracle attack. For BC 1.55 and older, in an environment where timings can be easily observed, it is possible with enough observations to identify when the decryption is failing due to padding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000345
- https://github.com/bcgit/bc-java/commit/21dcb3d9744c83dcf2ff8fcee06dbca7bfa4ef35#diff-4439ce586bf9a13bfec05c0d113b8098
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/advisories/GHSA-9gp4-qrff-c648
- https://lists.debian.org/debian-lts-announce/2018/07/msg00009.html
- https://security.netapp.com/advisory/ntap-20181127-0004
- https://usn.ubuntu.com/3727-1
- https://www.oracle.com/security-alerts/cpuoct2020.html
