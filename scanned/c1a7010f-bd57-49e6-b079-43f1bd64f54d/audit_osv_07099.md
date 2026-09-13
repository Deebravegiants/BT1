# [H] BIT-nifi-2021-20190

## Summary
Severity: High
Advisory: BIT-nifi-2021-20190
Aliases: CVE-2021-20190, GHSA-5949-rw7g-wx7w
Ecosystem: Bitnami
Published: 2025-09-12
Source: https://osv.dev/vulnerability/BIT-nifi-2021-20190
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.7.0

## Details
A flaw was found in jackson-databind before 2.9.10.7. FasterXML mishandles the interaction between serialization gadgets and typing. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1916633
- https://github.com/FasterXML/jackson-databind/issues/2854
- https://lists.apache.org/thread.html/r380e9257bacb8551ee6fcf2c59890ae9477b2c78e553fa9ea08e9d9a%40%3Ccommits.nifi.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/04/msg00025.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-20190
- https://security.netapp.com/advisory/ntap-20210219-0008/
- https://www.oracle.com//security-alerts/cpujul2021.html
