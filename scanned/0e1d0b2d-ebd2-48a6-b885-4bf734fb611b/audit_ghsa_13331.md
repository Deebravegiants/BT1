# [C] Deserialization vulnerability in Helix workflow and REST

## Summary
Severity: Critical
Advisory: GHSA-jhcr-hph9-g7wm
CVE: CVE-2023-38647
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-jhcr-hph9-g7wm
Type: github-advisory

## Affected
- Maven: `org.apache.helix:helix-core` — affected >=0 <1.3.0
- Maven: `org.apache.helix:helix-rest` — affected >=0 <1.3.0

## Details
An attacker can use SnakeYAML to deserialize java.net.URLClassLoader and make it load a JAR from a specified URL, and then deserialize javax.script.ScriptEngineManager to load code using that ClassLoader. This unbounded deserialization can likely lead to remote code execution. The code can be run in Helix REST start and Workflow creation.

Affect all the versions lower and include 1.2.0.

Affected products: helix-core, helix-rest

Mitigation: Short term, stop using any YAML based configuration and workflow creation.
                  Long term, all Helix version bumping up to 1.3.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38647
- https://github.com/apache/helix/commit/09d210fa29b18f3b4de8d32f2369dc2b31f71f43
- https://github.com/apache/helix/commit/eabfda26b18c72f4f945dcaac5756665c6a2cdac
- https://lists.apache.org/thread/zyqxhv0lc2z9w3tgr8ttrdy2zfh5jvc4
