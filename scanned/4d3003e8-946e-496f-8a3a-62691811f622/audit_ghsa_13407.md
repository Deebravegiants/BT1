# [H] Apache ShardingSphere-Agent Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-3cxh-xp3g-jxjm
CVE: CVE-2023-28754
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-19
Source: https://github.com/advisories/GHSA-3cxh-xp3g-jxjm
Type: github-advisory

## Affected
- Maven: `org.apache.shardingsphere:shardingsphere` — affected >=0 <5.4.0

## Details
Deserialization of Untrusted Data vulnerability in Apache ShardingSphere-Agent, which allows attackers to execute arbitrary code by constructing a special YAML configuration file.

The attacker needs to have permission to modify the ShardingSphere Agent YAML configuration file on the target machine, and the target machine can access the URL with the arbitrary code JAR.
An attacker can use SnakeYAML to deserialize java.net.URLClassLoader and make it load a JAR from a specified URL, and then deserialize javax.script.ScriptEngineManager to load code using that ClassLoader. When the ShardingSphere JVM process starts and uses the ShardingSphere-Agent, the arbitrary code specified by the attacker will be executed during the deserialization of the YAML configuration file by the Agent.

This issue affects ShardingSphere-Agent: through 5.3.2. This vulnerability is fixed in Apache ShardingSphere 5.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28754
- https://github.com/apache/shardingsphere
- https://lists.apache.org/thread/p8onhqox5kkwow9lc6gs03z28wtyp1cg
- http://www.openwall.com/lists/oss-security/2023/07/19/3
