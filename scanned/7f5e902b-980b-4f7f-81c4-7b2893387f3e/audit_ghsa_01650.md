# [H] Improper input validation in Apache Olingo

## Summary
Severity: High
Advisory: GHSA-477x-w7m6-c6ph
CVE: CVE-2019-17555
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-02-04
Source: https://github.com/advisories/GHSA-477x-w7m6-c6ph
Type: github-advisory

## Affected
- Maven: `org.apache.olingo:odata-client-core` — affected >=4.0.0 <4.7.0

## Details
The AsyncResponseWrapperImpl class in Apache Olingo versions 4.0.0 to 4.6.0 reads the Retry-After header and passes it to the Thread.sleep() method without any check. If a malicious server returns a huge value in the header, then it can help to implement a DoS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17555
- https://github.com/apache/olingo-odata4/pull/61
- https://issues.apache.org/jira/browse/OLINGO-1411
- https://mail-archives.apache.org/mod_mbox/olingo-user/201912.mbox/%3CCAGSZ4d65UmudJ_MQkFXEv9YY_wwZbRA3sgtNDzMoLM51Qh%3DRCA%40mail.gmail.com%3E
