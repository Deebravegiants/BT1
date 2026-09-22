# [H] Improper Certificate Validation in Apache Beam

## Summary
Severity: High
Advisory: GHSA-2m7g-9q74-9m3q
CVE: CVE-2020-1929
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-05-06
Source: https://github.com/advisories/GHSA-2m7g-9q74-9m3q
Type: github-advisory

## Affected
- Maven: `org.apache.beam:beam-sdks-java-io-mongodb` — affected >=2.10.0 <2.17.0

## Details
The Apache Beam MongoDB connector in versions 2.10.0 to 2.16.0 has an option to disable SSL trust verification. However this configuration is not respected and the certificate verification disables trust verification in every case. This exclusion also gets registered globally which disables trust checking for any code running in the same JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1929
- https://github.com/apache/beam/commit/a7dd23d95d2d214b4110781b5a28802bd43b834b
- https://github.com/apache/beam
- https://lists.apache.org/thread.html/rdd0e85b71bf0274471b40fa1396d77f7b2d1165eaea4becbdc69aa04%40%3Cuser.beam.apache.org%3E
