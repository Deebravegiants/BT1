# [C] Apache Commons BCEL vulnerable to out-of-bounds write

## Summary
Severity: Critical
Advisory: GHSA-97xg-phpr-rg8q
CVE: CVE-2022-42920
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-07
Source: https://github.com/advisories/GHSA-97xg-phpr-rg8q
Type: github-advisory

## Affected
- Maven: `org.apache.bcel:bcel` — affected >=0 <6.6.0

## Details
Apache Commons BCEL has a number of APIs that would normally only allow changing specific class characteristics. However, due to an out-of-bounds writing issue, these APIs can be used to produce arbitrary bytecode. This could be abused in applications that pass attacker-controllable data to those APIs, giving the attacker more control over the resulting bytecode than otherwise expected. Update to Apache Commons BCEL 6.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42920
- https://github.com/apache/commons-bcel/pull/147
- https://github.com/apache/commons-bcel
- https://issues.apache.org/jira/browse/BCEL-363
- https://lists.apache.org/thread/lfxk7q8qmnh5bt9jm6nmjlv5hsxjhrz4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LX3HEB4TV2BVCGDTK5BCLSYOZNQTOBN4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QAMRHAKGIKZNHRBB4VLYTOIOIMMXCUCD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QMVX6COVXZVS5GPWDODIRW6Z2GE7RPAQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LX3HEB4TV2BVCGDTK5BCLSYOZNQTOBN4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QAMRHAKGIKZNHRBB4VLYTOIOIMMXCUCD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QMVX6COVXZVS5GPWDODIRW6Z2GE7RPAQ
- https://security.gentoo.org/glsa/202401-25
- http://www.openwall.com/lists/oss-security/2022/11/07/2
