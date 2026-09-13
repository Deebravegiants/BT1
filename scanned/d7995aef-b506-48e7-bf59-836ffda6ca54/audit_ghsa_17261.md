# [H] Apache HugeGraph-Server: RAFT and deserialization vulnerability

## Summary
Severity: High
Advisory: GHSA-q37j-3367-fwv7
CVE: CVE-2025-26866
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-q37j-3367-fwv7
Type: github-advisory

## Affected
- Maven: `org.apache.hugegraph:hg-pd-core` — affected >=0 <1.7.0

## Details
A remote code execution vulnerability exists where a malicious Raft node can exploit insecure Hessian deserialization within the PD store. The fix enforces IP-based authentication to restrict cluster membership and implements a strict class whitelist to harden the Hessian serialization process against object injection attacks.

Users are recommended to upgrade to version 1.7.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26866
- https://github.com/apache/incubator-hugegraph/pull/2735
- https://github.com/apache/incubator-hugegraph
- https://lists.apache.org/thread/ko8jkwbjbb99m45pg4sgo5xsm8gx9nsq
- http://www.openwall.com/lists/oss-security/2025/12/09/1
