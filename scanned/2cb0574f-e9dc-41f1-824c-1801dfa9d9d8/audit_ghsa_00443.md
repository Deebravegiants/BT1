# [H] In Bouncy Castle JCE Provider it is possible to inject extra elements in the sequence making up the signature and still have it validate

## Summary
Severity: High
Advisory: GHSA-4vhj-98r6-424h
CVE: CVE-2016-1000338
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-4vhj-98r6-424h
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk14` — affected >=1.38 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15` — affected >=1.38 <1.56
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=1.38 <1.56

## Details
In Bouncy Castle JCE Provider version 1.55 and earlier the DSA does not fully validate ASN.1 encoding of signature on verification. It is possible to inject extra elements in the sequence making up the signature and still have it validate, which in some cases may allow the introduction of 'invisible' data into a signed structure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000338
- https://github.com/bcgit/bc-java/commit/b0c3ce99d43d73a096268831d0d120ffc89eac7f#diff-3679f5a9d2b939d0d3ee1601a7774fb0
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/bcgit/bc-java
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451%40%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2018/07/msg00009.html
- https://security.netapp.com/advisory/ntap-20231006-0011
- https://usn.ubuntu.com/3727-1
- https://www.oracle.com/security-alerts/cpuoct2020.html
