# [H] In Bouncy Castle JCE Provider the DHIES implementation allowed the use of ECB mode

## Summary
Severity: High
Advisory: GHSA-2j2x-hx4g-2gf4
CVE: CVE-2016-1000344
CWE: CWE-1310
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-2j2x-hx4g-2gf4
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=0 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.56

## Details
In the Bouncy Castle JCE Provider version 1.55 and earlier the DHIES implementation allowed the use of ECB mode. This mode is regarded as unsafe and support for it has been removed from the provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000344
- https://github.com/bcgit/bc-java/commit/9385b0ebd277724b167fe1d1456e3c112112be1f
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/advisories/GHSA-2j2x-hx4g-2gf4
- https://security.netapp.com/advisory/ntap-20181127-0004
- https://www.oracle.com/security-alerts/cpuoct2020.html
