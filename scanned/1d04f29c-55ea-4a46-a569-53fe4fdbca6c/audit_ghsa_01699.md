# [H] Polymorphic deserialization of malicious object in jackson-databind

## Summary
Severity: High
Advisory: GHSA-qmqc-x3r4-6v39
CVE: CVE-2019-14893
CWE: CWE-502
Ecosystem: Maven
Published: 2020-05-15
Source: https://github.com/advisories/GHSA-qmqc-x3r4-6v39
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.10

## Details
A flaw was discovered in FasterXML jackson-databind in all versions before 2.9.10 and 2.10.0, where it would permit polymorphic deserialization of malicious objects using the xalan JNDI gadget when used in conjunction with polymorphic type handling methods such as `enableDefaultTyping()` or when @JsonTypeInfo is using `Id.CLASS` or `Id.MINIMAL_CLASS` or in any other way which ObjectMapper.readValue might instantiate objects from unsafe sources. An attacker could use this flaw to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14893
- https://github.com/FasterXML/jackson-databind/issues/2469
- https://github.com/FasterXML/jackson-databind/commit/998efd708284778f29d83d7962a9bd935c228317
- https://access.redhat.com/errata/RHSA-2020:0729
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14893
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf1bbc0ea4a9f014cf94df9a12a6477d24a27f52741dbc87f2fd52ff2@%3Cissues.geode.apache.org%3E
- https://security.netapp.com/advisory/ntap-20200327-0006
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
