# [H] Missing Initialization of Resource in Apache Arrow

## Summary
Severity: High
Advisory: GHSA-cjw4-2w9r-r8mv
CVE: CVE-2019-12410
CWE: CWE-909
Ecosystem: PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cjw4-2w9r-r8mv
Type: github-advisory

## Affected
- PyPI: `pyarrow` — affected >=0.12.0 <0.15.1
- RubyGems: `red-arrow` — affected >=0.12.0 <0.15.1

## Details
While investigating UBSAN errors in https://github.com/apache/arrow/pull/5365 it was discovered Apache Arrow versions 0.12.0 to 0.14.1, left memory Array data uninitialized when reading RLE null data from parquet. This affected the C++, Python, Ruby and R implementations. The uninitialized memory could potentially be shared if are transmitted over the wire (for instance with Flight) or persisted in the streaming IPC and file formats.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12410
- https://github.com/advisories/GHSA-cjw4-2w9r-r8mv
- https://github.com/apache/arrow
- https://github.com/pypa/advisory-database/tree/main/vulns/pyarrow/PYSEC-2019-196.yaml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/red-arrow/CVE-2019-12410.yml
- https://lists.apache.org/thread.html/49f067b1c5fb7493d952580f0d2d032819ba351f7a78743c21126269@%3Cdev.arrow.apache.org%3E
- https://lists.apache.org/thread.html/efd8bbf57427d3c303b5316d208a335f8d0c0dbe0dc4c87cfa995073@%3Cannounce.apache.org%3E
- http://www.openwall.com/lists/oss-security/2019/11/08/1
