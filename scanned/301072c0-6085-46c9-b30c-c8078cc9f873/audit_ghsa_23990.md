# [H] Undertow Request Smuggling vulnerability

## Summary
Severity: High
Advisory: GHSA-5gg7-5wv8-4gcj
CVE: CVE-2017-12165
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5gg7-5wv8-4gcj
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <1.3.31
- Maven: `io.undertow:undertow-core` — affected >=1.4.0 <1.4.17
- Maven: `io.undertow:undertow-core` — affected >=2.0.0.Alpha1 <2.0.0.Beta1

## Details
It was discovered that Undertow before 1.4.17, 1.3.31 and 2.0.0 processes http request headers with unusual whitespaces which can cause possible http request smuggling.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12165
- https://github.com/undertow-io/undertow/commit/1e72647818c9fb31b693a953b1ae595a6c82eb7f
- https://github.com/undertow-io/undertow/commit/5b008b7ac312c6cdb76679ff58c43620bb79d44f
- https://github.com/undertow-io/undertow/commit/691440ee58259fba76711b60d56dde6679808bdc
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-12165
- https://github.com/undertow-io/undertow
- https://issues.redhat.com/browse/UNDERTOW-1251
