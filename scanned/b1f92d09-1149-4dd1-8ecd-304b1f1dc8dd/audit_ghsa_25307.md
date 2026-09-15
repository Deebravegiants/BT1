# [H] Crash when decoding malformed HTTP requests or malformed JSON payload

## Summary
Severity: High
Advisory: GHSA-95q3-pppp-r683
CVE: CVE-2018-1330
CWE: CWE-248
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-95q3-pppp-r683
Type: github-advisory

## Affected
- Maven: `org.apache.mesos:mesos` — affected >=1.4.0 <1.6.0

## Details
When parsing a malformed JSON payload, libprocess in Apache Mesos versions 1.4.0 to 1.5.0 might crash due to an uncaught exception. Parsing chunked HTTP requests with trailers can lead to a libprocess crash too because of the mistakenly planted assertion. A malicious actor can therefore cause a denial of service of Mesos masters rendering the Mesos-controlled cluster inoperable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1330
- https://lists.apache.org/thread.html/395cb6bcf367702acd1e580a1f39b56cdd7a5953d0368b4c1adb1dde@<dev.mesos.apache.org>
