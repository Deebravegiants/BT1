# [M] Insufficient Verification of Data Authenticity in Async Http Client

## Summary
Severity: Medium
Advisory: GHSA-8h53-fjgg-g42g
CVE: CVE-2013-7397
CWE: CWE-345
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8h53-fjgg-g42g
Type: github-advisory

## Affected
- Maven: `com.ning:async-http-client` — affected >=0 <1.9.0

## Details
Async Http Client (aka AHC or async-http-client) before 1.9.0 skips X.509 certificate verification unless both a keyStore location and a trustStore location are explicitly set, which allows man-in-the-middle attackers to spoof HTTPS servers by presenting an arbitrary certificate during use of a typical AHC configuration, as demonstrated by a configuration that does not send client certificates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7397
- https://github.com/AsyncHttpClient/async-http-client/issues/352
- https://github.com/AsyncHttpClient/async-http-client/commit/dfacb8e05d0822c7b2024c452554bd8e1d6221d8
- https://github.com/AsyncHttpClient/async-http-client
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-06-20
- http://openwall.com/lists/oss-security/2014/08/26/1
- http://rhn.redhat.com/errata/RHSA-2015-0850.html
- http://rhn.redhat.com/errata/RHSA-2015-0851.html
- http://rhn.redhat.com/errata/RHSA-2015-1176.html
- http://rhn.redhat.com/errata/RHSA-2015-1551.html
