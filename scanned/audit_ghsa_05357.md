# [C] Apache MINA: Critical Deserialization Allow-list Bypass via resolveProxyClass

## Summary
Severity: Critical
Advisory: GHSA-v3pr-hxpr-mfm8
CVE: CVE-2026-47065
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-v3pr-hxpr-mfm8
Type: github-advisory

## Affected
- Maven: `org.apache.mina:mina-core` — affected >=2.2.0 <2.2.8
- Maven: `org.apache.mina:mina-core` — affected >=2.1.0 <2.1.13
- Maven: `org.apache.mina:mina-core` — affected >=0 <2.0.29

## Details
ZDRES-232: resolveProxyClass Not Overridden - acceptMatchers Filter Bypass via java.lang.reflect.Proxy


Assessment: Fully addressed.


When the serialised stream contains a TC_PROXYCLASSDESC (the marker for a java.lang.reflect.Proxy ), JDK’s ObjectInputStream.readProxyDesc() is dispatched. JDK then calls the default  ObjectInputStream.resolveProxyClass(interfaces) implementation, which performs Class.forName(intf, false, latestUserDefinedLoader()) for EACH interface name and constructs the proxy class â€” bypassing the accepted classes list .


ZDRES-233: Class.forName(name, initialize=true, classLoader) in readClassDescriptor Triggers Static Initialiser of Allow-Listed Classes


Assessment: Fully addressed.


For ANY class on the allow-list, deserialising a stream that names it triggers the class’s (static initialiser) BEFORE any instance is constructed. This means an attacker who supplies a class name on the allow-list (e.g., the developer wrote accept(“com.myapp.*") , attacker supplies com.myapp.SomeClass ) causes <clinit> of SomeClass â€” and many real-world classes have side-effecting static initialisers


Both issues have been fixed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47065
- https://github.com/apache/mina
- https://lists.apache.org/thread/y7xj1bl8qo47p9bktb11hg5v6k1d4dyj
