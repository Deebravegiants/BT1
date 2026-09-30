# [H] XStream can be used for Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-mw36-7c6c-q4q2
CVE: CVE-2020-26217
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-11-16
Source: https://github.com/advisories/GHSA-mw36-7c6c-q4q2
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.14-java7

## Details
### Impact
The vulnerability may allow a remote attacker to run arbitrary shell commands only by manipulating the processed input stream.

### Patches
If you rely on XStream's default blacklist of the [Security Framework](https://x-stream.github.io/security.html#framework), you will have to use at least version 1.4.14.

### Workarounds
No user is affected, who followed the recommendation to setup XStream's Security Framework with a whitelist! Anyone relying on XStream's default blacklist can immediately switch to a whilelist for the allowed types to avoid the vulnerability.

Users of XStream 1.4.13 or below who still want to use XStream default blacklist can use a workaround depending on their version in use.

Users of XStream 1.4.13 can simply add two lines to XStream's setup code:
```Java
xstream.denyTypes(new String[]{ "javax.imageio.ImageIO$ContainsFilter" });
xstream.denyTypes(new Class[]{ java.lang.ProcessBuilder.class });
```
Users of XStream 1.4.12 to 1.4.7 who want to use XStream with a black list will have to setup such a list from scratch and deny at least the following types: _javax.imageio.ImageIO$ContainsFilter_, _java.beans.EventHandler_, _java.lang.ProcessBuilder_, _java.lang.Void_ and _void_.
```Java
xstream.denyTypes(new String[]{ "javax.imageio.ImageIO$ContainsFilter" });
xstream.denyTypes(new Class[]{ java.lang.ProcessBuilder.class, java.beans.EventHandler.class, java.lang.ProcessBuilder.class, java.lang.Void.class, void.class });
```
Users of XStream 1.4.6 or below can register an own converter to prevent the unmarshalling of the currently know critical types of the Java runtime. It is in fact an updated version of the workaround for CVE-2013-7285:
```Java
xstream.registerConverter(new Converter() {
  public boolean canConvert(Class type) {
    return type != null && (type == java.beans.EventHandler.class || type == java.lang.ProcessBuilder.class || type == java.lang.Void.class || void.class || type.getName().equals("javax.imageio.ImageIO$ContainsFilter") || Proxy.isProxy(type));
  }

  public Object unmarshal(HierarchicalStreamReader reader, UnmarshallingContext context) {
    throw new ConversionException("Unsupported type due to security reasons.");
  }

  public void marshal(Object source, HierarchicalStreamWriter writer, MarshallingContext context) {
    throw new ConversionException("Unsupported type due to security reasons.");
  }
}, XStream.PRIORITY_LOW);
```

### Credits
Chen L found and reported the issue to XStream and provided the required information to reproduce it.  He was supported by Zhihong Tian and Hui Lu, both from Guangzhou University.

### References
See full information about the nature of the vulnerability and the steps to reproduce it in XStream's documentation for [CVE-2020-26217](https://x-stream.github.io/CVE-2020-26217.html).

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [XStream](https://github.com/x-stream/xstream/issues)
* Contact us at [XStream Google Group](https://groups.google.com/group/xstream-user)

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-mw36-7c6c-q4q2
- https://nvd.nist.gov/vuln/detail/CVE-2020-26217
- https://github.com/x-stream/xstream/commit/0fec095d534126931c99fd38e9c6d41f5c685c1a
- https://x-stream.github.io/CVE-2020-26217.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.debian.org/security/2020/dsa-4811
- https://security.netapp.com/advisory/ntap-20210409-0004
- https://lists.debian.org/debian-lts-announce/2020/12/msg00001.html
- https://lists.apache.org/thread.html/redde3609b89b2a4ff18b536a06ef9a77deb93d47fda8ed28086fa8c3@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r826a006fda71cc96fc87b6eca4b5d195f19a292ad36cea501682c38c@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r7c9fc255edc0b9cd9567093d131f6d33fde4c662aaf912460ef630e9@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/r2de526726e7f4db4a7cb91b7355070779f51a84fd985c6529c2f4e9e@%3Cissues.activemq.apache.org%3E
- https://github.com/x-stream/xstream
