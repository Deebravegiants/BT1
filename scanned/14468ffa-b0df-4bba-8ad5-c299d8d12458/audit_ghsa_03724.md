# [C] XML External Entity Reference in mchange:c3p0

## Summary
Severity: Critical
Advisory: GHSA-q485-j897-qc27
CVE: CVE-2018-20433
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-07
Source: https://github.com/advisories/GHSA-q485-j897-qc27
Type: github-advisory

## Affected
- Maven: `com.mchange:c3p0` — affected >=0 <0.9.5.3

## Details
c3p0 0.9.5.2 allows XXE in extractXmlConfigFromInputStream in com/mchange/v2/c3p0/cfg/C3P0ConfigXmlUtils.java during initialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20433
- https://github.com/zhutougg/c3p0/commit/2eb0ea97f745740b18dd45e4a909112d4685f87b
- https://github.com/advisories/GHSA-q485-j897-qc27
- https://github.com/zhutougg/c3p0
- https://lists.debian.org/debian-lts-announce/2018/12/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BFIVX6HOVNLAM7W3SUAMHYRNLCVQSAWR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQ47OFV57Y2DAHMGA5H3JOL4WHRWRFN4
