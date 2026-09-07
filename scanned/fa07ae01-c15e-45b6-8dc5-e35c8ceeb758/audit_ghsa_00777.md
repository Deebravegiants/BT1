# [C] Improper implementation of the session fixation protection in Infinispan

## Summary
Severity: Critical
Advisory: GHSA-6x3v-rw2q-9gx7
CVE: CVE-2019-10158
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-21
Source: https://github.com/advisories/GHSA-6x3v-rw2q-9gx7
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-core` — affected >=0 <9.4.15.Final

## Details
A flaw was found in Infinispan through version 9.4.14.Final. An improper implementation of the session fixation protection in the Spring Session integration can result in incorrect session handling.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10158
- https://github.com/infinispan/infinispan/pull/6960
- https://github.com/infinispan/infinispan/pull/7025
- https://github.com/infinispan/infinispan/pull/7043
- https://github.com/infinispan/infinispan/commit/4b381c5910265972ccaabefbdbd16a2b929f6b72
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10158
- https://github.com/infinispan/infinispan
- https://github.com/infinispan/infinispan/commits/9.4.15.Final
- https://security.netapp.com/advisory/ntap-20231227-0009
