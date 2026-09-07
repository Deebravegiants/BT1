# [H] Exposure of Sensitive Information in Apache Storm Logviewer

## Summary
Severity: High
Advisory: GHSA-r9pv-hg64-jqrp
CVE: CVE-2019-0202
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r9pv-hg64-jqrp
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-core` — affected >=0.9.1-incubating <1.2.3

## Details
The Apache Storm Logviewer daemon exposes HTTP-accessible endpoints to read/search log files on hosts running Storm. In Apache Storm versions 0.9.1-incubating to 1.2.2, it is possible to read files off the host's file system that were not intended to be accessible via these endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0202
- https://github.com/apache/storm
- https://lists.apache.org/thread.html/220f1a77ff20749326a4c130446c5521db854da0afe81d1974b8109f@%3Cuser.storm.apache.org%3E
