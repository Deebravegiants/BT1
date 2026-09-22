# [H] kafka-python vulnerable to denial of service through an unbounded SCRAM iteration count

## Summary
Severity: High
Advisory: GHSA-2jcm-hq8r-84wx
CVE: CVE-2026-10143
CWE: CWE-400, CWE-606
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-2jcm-hq8r-84wx
Type: github-advisory

## Affected
- PyPI: `kafka-python` — affected >=0 <2.3.2

## Details
kafka-python prior to 2.3.2 contains a denial-of-service vulnerability in SCRAM authentication handling that allows a malicious or machine-in-the-middle broker to freeze the client event loop by supplying an excessively large iteration count. In scram.py, ScramClient.process_server_first_message() passes the broker-controlled SCRAM iteration count directly to hashlib.pbkdf2_hmac() without validation, blocking producer sends, consumer polls, admin operations, and heartbeats, which can cause consumer group eviction and repeated reconnect failures.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10143
- https://github.com/dpkp/kafka-python/pull/3026
- https://github.com/dpkp/kafka-python/pull/3019
- https://github.com/dpkp/kafka-python/commit/74400d7ef1b54ad24d4b8170c23b58d1cab65e4f
- https://github.com/dpkp/kafka-python/commit/6e4831444f972d169cdd11f5c8d50333cea3f19b
- https://www.vulncheck.com/advisories/kafka-python-prior-to-dos-via-scram-iteration-count-in-scram-py
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-10143.json
- https://github.com/pypa/advisory-database/tree/main/vulns/kafka-python/PYSEC-2026-2191.yaml
- https://github.com/dpkp/kafka-python/releases/tag/2.3.2
- https://github.com/dpkp/kafka-python
- https://bugzilla.redhat.com/show_bug.cgi?id=2487722
- https://access.redhat.com/security/cve/CVE-2026-10143
- https://access.redhat.com/errata/RHSA-2026:42796
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/errata/RHSA-2026:33683
- https://access.redhat.com/errata/RHSA-2026:30076
- https://access.redhat.com/errata/RHSA-2026:28571
