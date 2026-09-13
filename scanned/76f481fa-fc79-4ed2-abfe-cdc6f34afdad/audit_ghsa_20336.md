# [H] SystemDS CPU exhaustion vulnerability

## Summary
Severity: High
Advisory: GHSA-m43h-hfrq-x8wx
CVE: CVE-2022-26477
CWE: CWE-400
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-28
Source: https://github.com/advisories/GHSA-m43h-hfrq-x8wx
Type: github-advisory

## Affected
- Maven: `org.apache.systemds:systemds` — affected >=0 <2.2.2
- PyPI: `systemds` — affected >=0 <2.2.2

## Details
The Security Team noticed that the termination condition of the for loop in the readExternal method is a controllable variable, which, if tampered with, may lead to CPU exhaustion. As a fix, we added an upper bound and termination condition in the read and write logic. We classify it as a "low-priority but useful improvement". SystemDS is a distributed system and needs to serialize/deserialize data but in many code paths (e.g., on Spark broadcast/shuffle or writing to sequence files) the byte stream is anyway protected by additional CRC fingerprints. In this particular case though, the number of decoders is upper-bounded by twice the number of columns, which means an attacker would need to modify two entries in the byte stream in a consistent manner. By adding these checks robustness was strictly improved with almost zero overhead. These code changes are available in versions higher than 2.2.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26477
- https://github.com/advisories/GHSA-m43h-hfrq-x8wx
- https://github.com/apache/systemds
- https://github.com/pypa/advisory-database/tree/main/vulns/systemds/PYSEC-2022-222.yaml
- https://lists.apache.org/thread/r4x2d2r6d4zykdrrx6s2l4qbxgzws0z3
- https://security.netapp.com/advisory/ntap-20220812-0003
