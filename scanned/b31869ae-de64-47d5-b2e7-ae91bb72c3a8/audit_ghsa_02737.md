# [M] Encoded URIs can access WEB-INF directory in Eclipse Jetty

## Summary
Severity: Medium
Advisory: GHSA-vjv5-gp2w-65vm
CVE: CVE-2021-34429
CWE: CWE-200, CWE-551, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-07-19
Source: https://github.com/advisories/GHSA-vjv5-gp2w-65vm
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-webapp` — affected >=9.4.37 <9.4.43
- Maven: `org.eclipse.jetty:jetty-webapp` — affected >=10.0.1 <10.0.6
- Maven: `org.eclipse.jetty:jetty-webapp` — affected >=11.0.1 <11.0.6

## Details
### Description
URIs can be crafted using some encoded characters to access the content of the `WEB-INF` directory and/or bypass some security constraints.
This is a variation of the vulnerability reported in [CVE-2021-28164](https://nvd.nist.gov/vuln/detail/CVE-2021-28164)/[GHSA-v7ff-8wcx-gmc5](https://github.com/eclipse/jetty.project/security/advisories/GHSA-v7ff-8wcx-gmc5).

### Impact
The default compliance mode allows requests with URIs that contain a %u002e segment to access protected resources within the WEB-INF directory. For example, a request to `/%u002e/WEB-INF/web.xml` can retrieve the web.xml file. This can reveal sensitive information regarding the implementation of a web application.  Similarly, an encoded null character can prevent correct normalization so that /.%00/WEB-INF/web.xml cal also retrieve the web.xml file.

### Workarounds
Some Jetty [rewrite rules](https://www.eclipse.org/jetty/documentation/jetty-9/index.html#rewrite-handler) can be deployed to rewrite any request containing encoded dot segments or null characters in the raw request URI, to a known not found resource:
```xml
<Call name="addRule">
  <Arg>
    <New class="org.eclipse.jetty.rewrite.handler.RewriteRegexRule">
      <Set name="regex">.*/(?:\.+/)+.*</Set>
      <Set name="replacement">/WEB-INF/Not-Found</Set>
    </New>
  </Arg>
</Call>
<Call name="addRule">
  <Arg>
    <New class="org.eclipse.jetty.rewrite.handler.ValidUrlRule"/>
  </Arg>
</Call>
```

### Analysis
Prior to 9.4.37, Jetty was protected from this style of attack by two lines of defense:
 + URIs were decoded first and then normalized for `.` and `..` sequences. Whilst this is not according to the RFC, it did remove relative segments that were encoded or parameterized and made the resulting URI paths safe from any repeated normalization (often done by URI manipulation and file system mapping).
 + The `FileResource` class treated any difference between absolute path and canonical path of a resource as an alias, and thus the resource would not be served by default.

Prior to 9.4.37, the `FileResource` class was replaced by the `PathResource` class that did not treat normalization differences as aliases.  Then release 9.4.37 updated the URI parsing to be compliant with the RFC, in that normalization is done before decoding.   This allowed various encodings or adornments to relative path segments that would not be normalized by the pure RFC URI normalization, but were normalized by the file system, thus allowing protected resources to be accessed via an alias.  Specifically by decoding URIs after normalization, it left them vulnerable to any subsequent normalization (potentially after checking security constraints) changing the URI singificantly.  Such extra normalization is often down by URI manipulation code and file systems.

With Jetty releases 9.4.43, 10.0.6, 11.0.6, we have restored several lines of defense:
 + URIs are first decoded and then normalized which is not strictly according to the current RFC.  Since the normalization is done after decoding, the URI paths produced are safe from further normalisation and the referenced resource cannot easily be so changed after passing security constraints.
 + During URI parsing checks are made for some specific segments/characters that are possible to be seen ambiguously by an application (e.g. encode dot segments, encoded separators, empty segments, parameterized dot segments and/or null characters). So even though Jetty code handles these URIs correctly, there is a risk that an application may not do so, thus such requests are rejected with a 400 Bad Request unless a specific compliance mode is set.
 + Once decoded and normalized by initial URI processing, Jetty will not decode or normalize a received URI again within its own resource handling. This avoids to possibility of double decode attacks.
 + The `ContextHandler.getResource(String path)` method always checks that the passed path is normalized, only accepting a non normal path if approved by an AliasChecker.  This is the method that is directly used by Jetty resource serving.
 + The API methods like `ServletContext.getResource(String path)` will normalize the  prior to calling `ContextHandler.getResource(String path)`. This allows applications to use non normal paths.
 + The `PathResource` class now considers any difference in normal/canonical name between a request resource name and the found resource name  to be an alias, which will only be served if approved by an explicit `AliasChecker`

In summary, the defense is a front line of detection of specific known URI alias attacks, with the last line defense of not allowing any aliasing of resources.

Many thanks to @cangqingzhe from @CloverSecLabs for reporting this issue.

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-vjv5-gp2w-65vm
- https://nvd.nist.gov/vuln/detail/CVE-2021-34429
- https://lists.apache.org/thread.html/r763840320a80e515331cbc1e613fa93f25faf62e991974171a325c82@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r7dd079fa0ac6f47ba1ad0af98d7d0276547b8a4e005f034fb1016951@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r833a4c8bdbbfeb8a2cd38238e7b59f83edd5c1a0e508b587fc551a46@%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r8e6c116628c1277c3cf132012a66c46a0863fa2a3037c0707d4640d4@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r90e7b4c42a96d74c219e448bee6a329ab0cd3205c44b63471d96c3ab@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r9d245c6c884bbc804a472116d730c1a01676bf24f93206a34923fc64@%3Ccommits.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r9e6158d72ef25077c2dc59fbddade2eacf7d259a2556c97a989f2fe8@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rb33d65c3e5686f2e3b9bb8a032a44163b2f2ad9d31a8727338f213c1@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rc26807be68748b3347decdcd03ae183622244b0b4cb09223d4b7e500@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rcb157f55b9ae41b3076801de927c6fca1669c6d8eaf11a9df5dbeb46@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rcea249eb7a0d243f21696e4985de33f3780399bf7b31ea1f6d489b8b@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/re01890eef49d4201018f2c97e26536e3e75f441ecdbcf91986c3bc17@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/re3de01414ccf682fe0951205f806dd8e94440798fd64c55a4941de3e@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/re5e9bb535db779506013ef8799dc2a299e77cdad6668aa94c456dba6@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/re850203ef8700cb826534dd4a1cb9f5b07bb8f6f973b39ff7838d3ba@%3Cissues.hbase.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210819-0006
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
