# [H] Uncontrolled Resource Consumption in Apache Thrift

## Summary
Severity: High
Advisory: GHSA-g2fg-mr77-6vrm
CVE: CVE-2020-13949
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-g2fg-mr77-6vrm
Type: github-advisory

## Affected
- Maven: `org.apache.thrift:libthrift` — affected >=0.9.3 <0.14.0

## Details
In Apache Thrift 0.9.3 to 0.13.0, malicious RPC clients could send short messages which would result in a large memory allocation, potentially leading to denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13949
- https://github.com/apache/hbase/pull/2958
- https://lists.apache.org/thread.html/rb3574bc1036b577b265be510e6b208f0a5d5d84cd7198347dc8482df@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/raea1bb8cf2eb39c5e10543f547bdbbdbb563c2ac6377652f161d4e37@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rae95c2234b6644bfd666b2671a1b42a09f38514d0f27cca3c7d5d55a@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/rada9d2244a66ede0be29afc5d5f178a209f9988db56b9b845d955741@%3Ccommits.hbase.apache.org%3E
- https://lists.apache.org/thread.html/rad635e16b300cf434280001ee6ecd2ed2c70987bf16eb862bfa86e02@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/race178e9500ab8a5a6112667d27c48559150cadb60f2814bc67c40af@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/ra9f7c755790313e1adb95d29794043fb102029e803daf4212ae18063@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/ra7371efd8363c1cd0f5331aafd359a808cf7277472b8616d7b392128@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/ra3f7f06a1759c8e2985ed24ae2f5483393c744c1956d661adc873f2c@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r9ec75f690dd60fec8621ba992290962705d5b7f0d8fd0a42fab0ac9f@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/r9b51e7c253cb0989b4c03ed9f4e5f0478e427473357209ccc4d08ebf@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r995b945cc8f6ec976d8c52d42ba931a688b45fb32cbdde715b6a816a@%3Cuser.thrift.apache.org%3E
- https://lists.apache.org/thread.html/r950ced188d62320fdb84d9e2c6ba896328194952eff7430c4f55e4b0@%3Cissues.hive.apache.org%3E
- https://lists.apache.org/thread.html/r93f23f74315e009f4fb68ef7fc794dceee42cf87fe6613814dcd8c70@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r90b4473950e26607ed77f3d70f120166f6a36a3f80888e4eeabcaf91@%3Cissues.solr.apache.org%3E
- https://lists.apache.org/thread.html/r8dfbefcd606af6737b62461a45a9af9222040b62eab474ff2287cf75@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r89fdd39965efb7c6d22bc21c286d203252cea476e1782724aca0748e@%3Cuser.thrift.apache.org%3E
- https://lists.apache.org/thread.html/r890b8ec5203d70a59a6b1289420d46938d9029ed706aa724978789be@%3Cissues.hbase.apache.org%3E
