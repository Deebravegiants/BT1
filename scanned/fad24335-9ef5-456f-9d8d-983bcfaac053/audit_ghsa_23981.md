# [M] Uncontrolled Resource Consumption in Apache Commons Compress

## Summary
Severity: Medium
Advisory: GHSA-6fxm-66hq-fc96
CVE: CVE-2012-2098
CWE: CWE-400
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6fxm-66hq-fc96
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-compress` — affected >=0 <1.4.1

## Details
Algorithmic complexity vulnerability in the sorting algorithms in bzip2 compressing stream (BZip2CompressorOutputStream) in Apache Commons Compress before 1.4.1 allows remote attackers to cause a denial of service (CPU consumption) via a file with many repeating inputs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2098
- https://github.com/apache/commons-compress/commit/020c03d8ef579e80511023fb46ece30e9c3dd27d
- https://github.com/apache/commons-compress/commit/0600296ab8f8a0bbdfedd483f51b38005eb8e34e
- https://github.com/apache/commons-compress/commit/1ce57d976c4f25fe99edcadf079840c278f3cb84
- https://github.com/apache/commons-compress/commit/2ab2fcb356753927afaa731b9d2dcc47d3083408
- https://github.com/apache/commons-compress/commit/654222e628097763ee6ca561ae77be5c06666173
- https://github.com/apache/commons-compress/commit/6ced422bf5eca3aac05396367bafb33ec21bf74e
- https://github.com/apache/commons-compress/commit/6e95697e783767f3549f00d7d2e1b002eac4a3d4
- https://github.com/apache/commons-compress/commit/8f702469cbf4c451b6dea349290bc4af0f6f76c7
- https://github.com/apache/commons-compress/commit/b06f7b41c936ef1a79589d16ea5c1d8b93f71f66
- https://github.com/apache/commons-compress/commit/cca0e6e5341aacddefd4c4d36cef7cbdbc2a8777
- https://github.com/apache/commons-compress/commit/ea31005111f0abede7e43e4ba0012e62e0808b22
- https://github.com/apache/commons-compress/commit/fdd7459bc5470e90024dbe762249166481cce769
- https://web.archive.org/web/20140724002926/http://secunia.com/advisories/49286
- https://web.archive.org/web/20140724023114/http://secunia.com/advisories/49255
- https://web.archive.org/web/20200517014414/http://www.securitytracker.com/id?1027096
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://web.archive.org/web/20130525085523/http://www.securityfocus.com/bid/53676
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5@<solr-user.lucene.apache.org>
- https://github.com/apache/commons-compress
