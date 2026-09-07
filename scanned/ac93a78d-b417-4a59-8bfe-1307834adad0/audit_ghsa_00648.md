# [M] XStream vulnerable to an Arbitrary File Deletion on the local host when unmarshalling

## Summary
Severity: Medium
Advisory: GHSA-jfvx-7wrx-43fh
CVE: CVE-2020-26259
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-12-21
Source: https://github.com/advisories/GHSA-jfvx-7wrx-43fh
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.15

## Details
### Impact
The vulnerability may allow a remote attacker to delete arbitrary know files on the host as log as the executing process has sufficient rights only by manipulating the processed input stream.

### Patches
If you rely on XStream's default blacklist of the [Security Framework](https://x-stream.github.io/security.html#framework), you will have to use at least version 1.4.15.

### Workarounds
The reported vulnerability does only exist with a JAX-WS runtime on the classpath.

No user is affected, who followed the recommendation to setup XStream's Security Framework with a whitelist! Anyone relying on XStream's default blacklist can immediately switch to a whilelist for the allowed types to avoid the vulnerability.

Users of XStream 1.4.14 or below who still insist to use XStream default blacklist - despite that clear recommendation - can use a workaround depending on their version in use.

Users of XStream 1.4.14 can simply add two lines to XStream's setup code:
```Java
xstream.denyTypes(new String[]{ "jdk.nashorn.internal.objects.NativeString" });
xstream.denyTypesByRegExp(new String[]{ ".*\\.ReadAllStream\\$FileStream" });
```

Users of XStream 1.4.14 to 1.4.13 can simply add three lines to XStream's setup code:
```Java
xstream.denyTypes(new String[]{ "javax.imageio.ImageIO$ContainsFilter", "jdk.nashorn.internal.objects.NativeString" });
xstream.denyTypes(new Class[]{ java.lang.ProcessBuilder.class });
xstream.denyTypesByRegExp(new String[]{ ".*\\.ReadAllStream\\$FileStream" });
```
Users of XStream 1.4.12 to 1.4.7 who want to use XStream with a black list will have to setup such a list from scratch and deny at least the following types: _javax.imageio.ImageIO$ContainsFilter_, _java.beans.EventHandler_, _java.lang.ProcessBuilder_, _jdk.nashorn.internal.objects.NativeString.class_, _java.lang.Void_ and _void_ and deny several types by name pattern.
```Java
xstream.denyTypes(new String[]{ "javax.imageio.ImageIO$ContainsFilter", "jdk.nashorn.internal.objects.NativeString" });
xstream.denyTypes(new Class[]{ java.lang.ProcessBuilder.class, "jdk.nashorn.internal.objects.NativeString", java.beans.EventHandler.class, java.lang.ProcessBuilder.class, java.lang.Void.class, void.class });
xstream.denyTypesByRegExp(new String[]{ ".*\\$LazyIterator", "javax\\.crypto\\..*", ".*\\.ReadAllStream\\$FileStream" });
```
Users of XStream 1.4.6 or below can register an own converter to prevent the unmarshalling of the currently know critical types of the Java runtime. It is in fact an updated version of the workaround for CVE-2013-7285:
```Java
xstream.registerConverter(new Converter() {
  public boolean canConvert(Class type) {
    return type != null && (type == java.beans.EventHandler.class || type == java.lang.ProcessBuilder.class
        || type.getName().equals("javax.imageio.ImageIO$ContainsFilter") || type.getName().equals("jdk.nashorn.internal.objects.NativeString")
        || type == java.lang.Void.class || void.class || Proxy.isProxy(type))
        || type.getName().startsWith("javax.crypto.") || type.getName().endsWith("$LazyIterator") || type.getName().endsWith(".ReadAllStream$FileStream"));
  }

  public Object unmarshal(HierarchicalStreamReader reader, UnmarshallingContext context) {
    throw new ConversionException("Unsupported type due to security reasons.");
  }

  public void marshal(Object source, HierarchicalStreamWriter writer, MarshallingContext context) {
    throw new ConversionException("Unsupported type due to security reasons.");
  }
}, XStream.PRIORITY_LOW);
```
  
### For more information
If you have any questions or comments about this advisory:
* Open an issue in [XStream](https://github.com/x-stream/xstream/issues)
* Contact us at [XStream Google Group](https://groups.google.com/group/xstream-user)

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-jfvx-7wrx-43fh
- https://nvd.nist.gov/vuln/detail/CVE-2020-26259
- https://github.com/x-stream/xstream
- https://lists.apache.org/thread.html/r97993e3d78e1f5389b7b172ba9f308440830ce5f051ee62714a0aa34@%3Ccommits.struts.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/12/msg00042.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/22KVR6B5IZP3BGQ3HPWIO2FWWCKT3DHP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PVPHZA7VW2RRSDCOIPP2W6O5ND254TU7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QGXIU3YDPG6OGTDHMBLAFN7BPBERXREB
- https://security.netapp.com/advisory/ntap-20210409-0005
- https://www.debian.org/security/2021/dsa-4828
- https://x-stream.github.io/CVE-2020-26259.html
