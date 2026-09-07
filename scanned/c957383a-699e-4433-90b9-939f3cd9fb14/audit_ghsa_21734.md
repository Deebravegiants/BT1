# [H] Denial of Service by injecting highly recursive collections or maps in XStream

## Summary
Severity: High
Advisory: GHSA-rmr5-cpv2-vgjf
CVE: CVE-2021-43859
CWE: CWE-400, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-rmr5-cpv2-vgjf
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.19

## Details
### Impact
The vulnerability may allow a remote attacker to allocate 100% CPU time on the target system depending on CPU type or parallel execution of such a payload resulting in a denial of service only by manipulating the processed input stream.

### Patches
XStream 1.4.19 monitors and accumulates the time it takes to add elements to collections and throws an exception if a set threshold is exceeded.

### Workarounds
The attack uses the hash code implementation for collections and maps to force an exponential calculation time due to highly recursive structures with in the collection or map. Following types of the Java runtime are affected in Java versions available in December 2021:

- java.util.HashMap
- java.util.HashSet
- java.util.Hashtable
- java.util.LinkedHashMap
- java.util.LinkedHashSet
- java.util.Stack (older Java revisions only)
- java.util.Vector (older Java revisions only)
- Other third party collection implementations that use their element's hash code may also be affected

If your object graph does not use referenced elements at all, you may simply set the NO_REFERENCE mode:
```Java
XStream xstream = new XStream();
xstream.setMode(XStream.NO_REFERENCES);
```

If your object graph contains neither a Hashtable, HashMap nor a HashSet (or one of the linked variants of it) then you can use the security framework to deny the usage of these types:
```Java
XStream xstream = new XStream();
xstream.denyTypes(new Class[]{
 java.util.HashMap.class, java.util.HashSet.class, java.util.Hashtable.class, java.util.LinkedHashMap.class, java.util.LinkedHashSet.class
});
```

Unfortunately these types are very common. If you only use HashMap or HashSet and your XML refers these only as default map or set, you may additionally change the default implementation of java.util.Map and java.util.Set at unmarshalling time::
```Java
xstream.addDefaultImplementation(java.util.TreeMap.class, java.util.Map.class);
xstream.addDefaultImplementation(java.util.TreeSet.class, java.util.Set.class);
```
However, this implies that your application does not care about the implementation of the map and all elements are comparable.

### References
See full information about the nature of the vulnerability and the steps to reproduce it in XStream's documentation for [CVE-2021-43859](https://x-stream.github.io/CVE-2021-43859.html).

### Credits
The vulnerability was discovered and reported by r00t4dm at Cloud-Penetrating Arrow Lab.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [XStream](https://github.com/x-stream/xstream/issues)
* Contact us at [XStream Google Group](https://groups.google.com/group/xstream-user)

## References
- https://github.com/x-stream/xstream/security/advisories/GHSA-rmr5-cpv2-vgjf
- https://nvd.nist.gov/vuln/detail/CVE-2021-43859
- https://github.com/x-stream/xstream/commit/e8e88621ba1c85ac3b8620337dd672e0c0c3a846
- https://github.com/x-stream/xstream
- https://lists.debian.org/debian-lts-announce/2022/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VACQYG356OHUTD5WQGAQ4L2TTFTAV3SJ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XODFRE2ZL64FICBJDOPWOLPTSSAI4U7X
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VACQYG356OHUTD5WQGAQ4L2TTFTAV3SJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XODFRE2ZL64FICBJDOPWOLPTSSAI4U7X
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://x-stream.github.io/CVE-2021-43859.html
- http://www.openwall.com/lists/oss-security/2022/02/09/1
