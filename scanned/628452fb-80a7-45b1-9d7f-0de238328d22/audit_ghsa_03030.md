# [M] Local Information Disclosure Vulnerability in Netty on Unix-Like systems

## Summary
Severity: Medium
Advisory: GHSA-5mcr-gq6c-3hq2
CVE: CVE-2021-21290
CWE: CWE-378, CWE-379, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-02-08
Source: https://github.com/advisories/GHSA-5mcr-gq6c-3hq2
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.0.0 <4.1.59.Final
- Maven: `org.jboss.netty:netty` — affected >=0
- Maven: `io.netty:netty` — affected >=0

## Details
### Impact

When netty's multipart decoders are used local information disclosure can occur via the local system temporary directory if temporary storing uploads on the disk is enabled.

The CVSSv3.1 score of this vulnerability is calculated to be a [6.2/10](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N&version=3.1)

### Vulnerability Details

On unix-like systems, the temporary directory is shared between all user. As such, writing to this directory using APIs that do not explicitly set the file/directory permissions can lead to information disclosure. Of note, this does not impact modern MacOS Operating Systems.

The method `File.createTempFile` on unix-like systems creates a random file, but, by default will create this file with the permissions `-rw-r--r--`. Thus, if sensitive information is written to this file, other local users can read this information.

This is the case in netty's `AbstractDiskHttpData` is vulnerable.

https://github.com/netty/netty/blob/e5951d46fc89db507ba7d2968d2ede26378f0b04/codec-http/src/main/java/io/netty/handler/codec/http/multipart/AbstractDiskHttpData.java#L80-L101

`AbstractDiskHttpData` is used as a part of the `DefaultHttpDataFactory` class which is used by `HttpPostRequestDecoder` / `HttpPostMultiPartRequestDecoder`.

You may be affected by this vulnerability your project contains the following code patterns:

```java
channelPipeline.addLast(new HttpPostRequestDecoder(...));
```

```java
channelPipeline.addLast(new HttpPostMultiPartRequestDecoder(...));
```

### Patches

This has been patched in version `4.1.59.Final`.

### Workarounds

Specify your own `java.io.tmpdir` when you start the JVM or use `DefaultHttpDataFactory.setBaseDir(...)` to set the directory to something that is only readable by the current user.

### References

 - [CWE-378: Creation of Temporary File With Insecure Permissions](https://cwe.mitre.org/data/definitions/378.html)
 - [CWE-379: Creation of Temporary File in Directory with Insecure Permissions](https://cwe.mitre.org/data/definitions/379.html)

### Similar Vulnerabilities

Similar, but not the same.

 - JUnit 4 - https://github.com/junit-team/junit4/security/advisories/GHSA-269g-pwp5-87pp
 - Google Guava - https://github.com/google/guava/issues/4011
 - Apache Ant - https://nvd.nist.gov/vuln/detail/CVE-2020-1945
 - JetBrains Kotlin Compiler - https://nvd.nist.gov/vuln/detail/CVE-2020-15824

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [netty](https://github.com/netty/netty)
* Email us [here](mailto:netty-security@googlegroups.com)

### Original Report

> Hi Netty Security Team,
> 
> I've been working on some security research leveraging custom CodeQL queries to detect local information disclosure vulnerabilities in java applications. This was the result from running this query against the netty project:
> https://lgtm.com/query/7723301787255288599/
> 
> Netty contains three local information disclosure vulnerabilities, so far as I can tell.
> 
> One is here, where the private key for the certificate is written to a temporary file.
> 
> https://github.com/netty/netty/blob/e5951d46fc89db507ba7d2968d2ede26378f0b04/handler/src/main/java/io/netty/handler/ssl/util/SelfSignedCertificate.java#L316-L346
> 
> One is here, where the certificate is written to a temporary file.
> 
> https://github.com/netty/netty/blob/e5951d46fc89db507ba7d2968d2ede26378f0b04/handler/src/main/java/io/netty/handler/ssl/util/SelfSignedCertificate.java#L348-L371
> 
> The final one is here, where the 'AbstractDiskHttpData' creates a temporary file if the getBaseDirectory() method returns null. I believe that 'AbstractDiskHttpData' is used as a part of the file upload support? If this is the case, any files uploaded would be similarly vulnerable.
> 
> https://github.com/netty/netty/blob/e5951d46fc89db507ba7d2968d2ede26378f0b04/codec-http/src/main/java/io/netty/handler/codec/http/multipart/AbstractDiskHttpData.java#L91
> 
> All of these vulnerabilities exist because `File.createTempFile(String, String)` will create a temporary file in the system temporary directory if the 'java.io.tmpdir' system property is not explicitly set. It is my understanding that when java creates a file, by default, and using this method, the permissions on that file utilize the umask. In a majority of cases, this means that the file that java creates has the permissions: `-rw-r--r--`, thus, any other local user on that system can read the contents of that file.
> 
> Impacted OS:
> - Any OS where the system temporary directory is shared between multiple users. This is not the case for MacOS or Windows.
> 
> Mitigation.
> 
> Moving to the `Files` API instead will fix this vulnerability. 
> https://docs.oracle.com/javase/8/docs/api/java/nio/file/Files.html#createTempFile-java.nio.file.Path-java.lang.String-java.lang.String-java.nio.file.attribute.FileAttribute...-
> 
> This API will explicitly set the posix file permissions to something safe, by default.
> 
> I recently disclosed a similar vulnerability in JUnit 4:
> https://github.com/junit-team/junit4/security/advisories/GHSA-269g-pwp5-87pp
> 
> If you're also curious, this vulnerability in Jetty was also mine, also involving temporary directories, but is not the same vulnerability as in this case.
> https://github.com/eclipse/jetty.project/security/advisories/GHSA-g3wg-6mcf-8jj6
> 
> I would appreciate it if we could perform disclosure of this vulnerability leveraging the GitHub security advisories feature here. GitHub has a nice credit system that I appreciate, plus the disclosures, as you can see from the sampling above, end up looking very nice.
> https://github.com/netty/netty/security/advisories
> 
> This vulnerability disclosure follows Google's [90-day vulnerability disclosure policy](https://www.google.com/about/appsecurity/) (I'm not an employee of Google, I just like their policy). Full disclosure will occur either at the end of the 90-day deadline or whenever a patch is made widely available, whichever occurs first.
> 
> Cheers,
> Jonathan Leitschuh

## References
- https://github.com/netty/netty/security/advisories/GHSA-5mcr-gq6c-3hq2
- https://nvd.nist.gov/vuln/detail/CVE-2021-21290
- https://github.com/netty/netty/commit/c735357bf29d07856ad171c6611a2e1a0e0000ec
- https://github.com/netty/netty
- https://lists.apache.org/thread.html/r7bb3cdc192e9a6f863d3ea05422f09fa1ae2b88d4663e63696ee7ef5@%3Cdev.ranger.apache.org%3E
- https://lists.apache.org/thread.html/r9924ef9357537722b28d04c98a189750b80694a19754e5057c34ca48@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/ra0fc2b4553dd7aaf75febb61052b7f1243ac3a180a71c01f29093013@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/ra503756ced78fdc2136bd33e87cb7553028645b261b1f5c6186a121e@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rb06c1e766aa45ee422e8261a8249b561784186483e8f742ea627bda4@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rb51d6202ff1a773f96eaa694b7da4ad3f44922c40b3d4e1a19c2f325@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rb592033a2462548d061a83ac9449c5ff66098751748fcd1e2d008233@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rc0087125cb15b4b78e44000f841cd37fefedfda942fd7ddf3ad1b528@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rc488f80094872ad925f0c73d283d4c00d32def81977438e27a3dc2bb@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rcd163e421273e8dca1c71ea298dce3dd11b41d51c3a812e0394e6a5d@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rdba4f78ac55f803893a1a2265181595e79e3aa027e2e651dfba98c18@%3Cjira.kafka.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/02/msg00016.html
- https://security.netapp.com/advisory/ntap-20220210-0011
- https://www.debian.org/security/2021/dsa-4885
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
