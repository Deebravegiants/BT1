# [C] Apache Axis2/Java: deserialization of untrusted Data

## Summary
Severity: Critical
Advisory: CVE-2026-66713
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-66713
Type: osv

## Details
Deserialization of Untrusted Data (CWE-502) in the Tribes-based clustering component

  in Apache Software Foundation Apache Axis2/Java through 2.0.0 on Apache Tomcat

  (only when Tribes clustering is enabled, which is off by default) allows an

  unauthenticated remote attacker with network access to the clustering port to

  execute arbitrary code via a crafted serialized Java object delivered to the cluster

  channel and deserialized in

  org.apache.axis2.clustering.tribes.Axis2ChannelListener#messageReceived. Users are

  recommended to upgrade to version 2.0.1, which fixes this issue by removing the

  clustering feature entirely.

## References
- http://www.openwall.com/lists/oss-security/2026/07/28/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66713.json
- https://lists.apache.org/thread/fgggbv3sjjqw7p6q0j88gspt9b2rb728
- https://nvd.nist.gov/vuln/detail/CVE-2026-66713
- https://github.com/apache/axis-axis2-java-core/commit/e6f53b230bddcb40577c84ff290ba51e7265fa15
