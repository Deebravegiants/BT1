# [H] Path Traversal in Apache Flink

## Summary
Severity: High
Advisory: GHSA-395w-qhqr-9fr6
CVE: CVE-2020-17519
CWE: CWE-22, CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2021-01-06
Source: https://github.com/advisories/GHSA-395w-qhqr-9fr6
Type: github-advisory

## Affected
- Maven: `org.apache.flink:flink-runtime_2.11` — affected >=1.11.0 <1.11.3
- Maven: `org.apache.flink:flink-runtime_2.12` — affected >=1.11.0 <1.11.3

## Details
A change introduced in Apache Flink 1.11.0 (and released in 1.11.1 and 1.11.2 as well) allows attackers to read any file on the local filesystem of the JobManager through the REST interface of the JobManager process. Access is restricted to files accessible by the JobManager process. All users should upgrade to Flink 1.11.3 or 1.12.0 if their Flink instance(s) are exposed. The issue was fixed in commit b561010b0ee741543c3953306037f00d7a9f0801 from apache/flink:master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17519
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-17519
- https://lists.apache.org/thread.html/ra8c96bf3ccb4e491f9ce87ba35f134b4449beb2a38d1ce28fd89001f@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/ra8c96bf3ccb4e491f9ce87ba35f134b4449beb2a38d1ce28fd89001f%40%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r90890afea72a9571d666820b2fe5942a0a5f86be406fa31da3dd0922@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r90890afea72a9571d666820b2fe5942a0a5f86be406fa31da3dd0922%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r88f427865fb6aa6e6378efe07632a1906b430365e15e3b9621aabe1d@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r88f427865fb6aa6e6378efe07632a1906b430365e15e3b9621aabe1d%40%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r88b55f3ebf1f8f4e1cc61f030252aaef4b77060b56557a243abb92a1@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r88b55f3ebf1f8f4e1cc61f030252aaef4b77060b56557a243abb92a1%40%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r6843202556a6d0bce9607ebc02e303f68fc88e9038235598bde3b50d@%3Cuser.flink.apache.org%3E
- https://lists.apache.org/thread.html/r6843202556a6d0bce9607ebc02e303f68fc88e9038235598bde3b50d@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r6843202556a6d0bce9607ebc02e303f68fc88e9038235598bde3b50d@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r6843202556a6d0bce9607ebc02e303f68fc88e9038235598bde3b50d%40%3Cuser.flink.apache.org%3E
- https://lists.apache.org/thread.html/r6843202556a6d0bce9607ebc02e303f68fc88e9038235598bde3b50d%40%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r6843202556a6d0bce9607ebc02e303f68fc88e9038235598bde3b50d%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r4e1b72bfa789ea5bc20b8afe56119200ed25bdab0eb80d664fa5bfe2@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r4e1b72bfa789ea5bc20b8afe56119200ed25bdab0eb80d664fa5bfe2%40%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r2fc60b30557e4a537c2a6293023049bd1c49fd92b518309aa85a0398@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r2fc60b30557e4a537c2a6293023049bd1c49fd92b518309aa85a0398%40%3Cissues.flink.apache.org%3E
