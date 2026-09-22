# [C] Deserialization of Untrusted Data in apache-submarine

## Summary
Severity: Critical
Advisory: GHSA-8hcr-5x2g-9f7j
CVE: CVE-2023-46302
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-20
Source: https://github.com/advisories/GHSA-8hcr-5x2g-9f7j
Type: github-advisory

## Affected
- PyPI: `apache-submarine` — affected >=0.7.0 <0.8.0

## Details
Apache Software Foundation Apache Submarine has a bug when serializing against yaml. The bug is caused by snakeyaml  https://nvd.nist.gov/vuln/detail/CVE-2022-1471 .

Apache Submarine uses JAXRS to define REST endpoints.  In order to
handle YAML requests (using application/yaml content-type), it defines
a YamlEntityProvider entity provider that will process all incoming
YAML requests.  In order to unmarshal the request, the readFrom method
is invoked, passing the entityStream containing the user-supplied data in `submarine-server/server-core/src/main/java/org/apache/submarine/server/utils/YamlUtils.java`.
 
We have now fixed this issue in the new version by replacing to `jackson-dataformat-yaml`.
This issue affects Apache Submarine: from 0.7.0 before 0.8.0. Users are recommended to upgrade to version 0.8.0, which fixes this issue.
If using the version smaller than 0.8.0  and not want to upgrade, you can try cherry-pick PR  https://github.com/apache/submarine/pull/1054  and rebuild the submart-server image to fix this.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46302
- https://github.com/apache/submarine/pull/1054
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-submarine/PYSEC-2023-240.yaml
- https://issues.apache.org/jira/browse/SUBMARINE-1371
- https://lists.apache.org/thread/zf0wppzh239j4h131hm1dbswfnztxrr5
