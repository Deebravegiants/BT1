# [H] Remote code execution due to insecure deserialization

## Summary
Severity: High
Advisory: GHSA-4344-frcp-j22q
CVE: CVE-2013-2165
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4344-frcp-j22q
Type: github-advisory

## Affected
- Maven: `org.richfaces:richfaces` — affected >=3.1.0 <3.3.3
- Maven: `org.richfaces:richfaces` — affected >=4.0.0 <4.3.2

## Details
A flaw was found in the way JBoss RichFaces handled deserialization. A remote attacker could use this flaw to trigger the execution of the deserialization methods in any serializable class deployed on the server. This could lead to a variety of security impacts depending on the deserialization logic of these classes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2165
- https://access.redhat.com/security/cve/CVE-2013-2165
- https://bugzilla.redhat.com/show_bug.cgi?id=973570
- http://jvn.jp/en/jp/JVN38787103/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2013-000072
- http://packetstormsecurity.com/files/156663/Richsploit-RichFaces-Exploitation-Toolkit.html
- http://seclists.org/fulldisclosure/2020/Mar/21
