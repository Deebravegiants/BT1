# [M] c3p0 can, in combination with other libraries, compose to a "sink" for deserialization gadgets

## Summary
Severity: Medium
Advisory: GHSA-w6w4-rjh9-9r58
CVE: CVE-2026-55223
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-w6w4-rjh9-9r58
Type: github-advisory

## Affected
- Maven: `com.mchange:c3p0` — affected >=0 <0.14.0

## Details
### Impact

The JDBC spec defines the interface `DataSource`, with a method called `getConnection()`, and `ConnectionPoolDataSource`, with a method called `getPooledConnection()`. These methods are potentially dangerous. One way or another they trigger calls into JDBC drivers, which themselves are complicated, flexible tools which may be, and in practice sometimes have proven to be, susceptible to abuse.

Unfortunately, the JavaBean framework treats methods of this form, `getXXX()`, as JavaBean "properties", which JavaBean-related libraries often presume represent quick, safe-to-look-up, state or configuration.

Attackers therefore can construct malicious `DataSource` objects — objects whose calls to `getConnection()` or `getPooledConnection()` would trigger attacks via vulnerable JDBC drivers — and bundle them in contexts that automatically look up bean properties on deserialization. If an attacker can smuggle such an object in serialized form to a location from which an application will deserialize it, an attack is triggered.

It's not easy. It requires that a susceptible JDBC `DataSource` or `ConnectionPoolDataSource` be available on the application `CLASSPATH`, along with a susceptible JDBC driver, and a carrier that will automatically look up JavaBean properties on deserialization. In practice, the most common such carrier is the composition of a collection and a `Comparator` implementation that sorts based on JavaBean properties from Apache [`commons-beanutils`](https://commons.apache.org/proper/commons-beanutils/).

But c3p0 prior to 0.14.0 offered the susceptible JDBC `DataSource` or `ConnectionPoolDataSource`, supplying an essential component of the trigger.

### Patches

c3p0 versions 0.14.0 and above no longer participate in this class of attack, because they include explicit `BeanInfo` classes which exclude `connection` and `pooledConnection` from the list of "introspected" JavaBean properties. Since `getConnection()` and `getPooledConnection()` no longer define JavaBean properties, classes that promiscuously read JavaBean properties do not call them, and the attack is averted.

### Workarounds

If users can ensure the safety of all JDBC drivers on the application `CLASSPATH`, or that no libraries lie on the `CLASSPATH` that can be composed to trigger automatic JavaBean property lookups on deserialization, then this attack is prevented. Nevertheless, given the complexity of modern JDBC drivers and typical Java application transitive dependencies, it is strongly recommended that users upgrade to c3p0 version 0.14.0 or higher.

Some versions of this attack are foiled by [the stronger encapsulation and restriction of reflective access introduced in Java 16](https://softwaregarden.dev/en/posts/new-java/illegal-access-in-java-16/). Running applications on Java 16+ is therefore a potential mitigation.

This attack is described by [Hans-Martin Münch](https://mogwailabs.de/en/authors/hans-martin-muench/) in a blog post called "[Look Mama, no TemplatesImpl](https://mogwailabs.de/en/blog/2023/04/look-mama-no-templatesimpl/)".

## References
- https://github.com/swaldman/c3p0/security/advisories/GHSA-w6w4-rjh9-9r58
- https://nvd.nist.gov/vuln/detail/CVE-2026-55223
- https://github.com/swaldman/c3p0/commit/7b022c4b6694dabc6204254dc917af9c38f2cb27
- https://github.com/swaldman/c3p0
- https://github.com/swaldman/c3p0/releases/tag/v0.14.0
