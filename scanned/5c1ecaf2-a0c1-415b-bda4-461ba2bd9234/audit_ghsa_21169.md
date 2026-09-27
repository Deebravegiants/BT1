# [H] Jetty SslConnection does not release pooled ByteBuffers in case of errors

## Summary
Severity: High
Advisory: GHSA-8mpp-f3f7-xc28
CVE: CVE-2022-2191
CWE: CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-07
Source: https://github.com/advisories/GHSA-8mpp-f3f7-xc28
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=10.0.0 <10.0.10
- Maven: `org.eclipse.jetty:jetty-server` — affected >=11.0.0 <11.0.10

## Details
### Impact
`SslConnection` does not release `ByteBuffer`s in case of error code paths.
For example, TLS handshakes that require client-auth with clients that send expired certificates will trigger a TLS handshake errors and the `ByteBuffer`s used to process the TLS handshake will be leaked.

### Workarounds
Configure explicitly a `RetainableByteBufferPool` with `max[Heap|Direct]Memory` to limit the amount of memory that is leaked.
Eventually the pool will be full of "active" entries (the leaked ones) and will provide `ByteBuffer`s that will be GCed normally.

_With embedded-jetty_

``` java
int maxBucketSize = 1000;
long maxHeapMemory = 128 * 1024L * 1024L; // 128 MB
long maxDirectMemory = 128 * 1024L * 1024L; // 128 MB
RetainableByteBufferPool rbbp = new ArrayRetainableByteBufferPool(0, -1, -1, maxBucketSize, maxHeapMemory, maxDirectMemory);

server.addBean(rbbp); // make sure the ArrayRetainableByteBufferPool is added before the server is started
server.start();
```

_With jetty-home/jetty-base_

Create a `${jetty.base}/etc/retainable-byte-buffer-config.xml`

``` xml
<?xml version="1.0"?>
<!DOCTYPE Configure PUBLIC "-//Jetty//Configure//EN" "https://www.eclipse.org/jetty/configure_10_0.dtd">

<Configure id="Server" class="org.eclipse.jetty.server.Server">
  <Call name="addBean">
    <Arg>
      <New class="org.eclipse.jetty.io.ArrayRetainableByteBufferPool">
        <Arg type="int"><Property name="jetty.byteBufferPool.minCapacity" default="0"/></Arg>
        <Arg type="int"><Property name="jetty.byteBufferPool.factor" default="-1"/></Arg>
        <Arg type="int"><Property name="jetty.byteBufferPool.maxCapacity" default="-1"/></Arg>
        <Arg type="int"><Property name="jetty.byteBufferPool.maxBucketSize" default="1000"/></Arg>
        <Arg type="long"><Property name="jetty.byteBufferPool.maxHeapMemory" default="128000000"/></Arg>
        <Arg type="long"><Property name="jetty.byteBufferPool.maxDirectMemory" default="128000000"/></Arg>
      </New>
    </Arg>
  </Call>
</Configure>
```

And then reference it in `${jetty.base}/start.d/retainable-byte-buffer-config.ini`

```
etc/retainable-byte-buffer-config.xml
```


### References
https://github.com/eclipse/jetty.project/issues/8161

### For more information
* Email us at [security@webtide.com](mailto:security@webtide.com)

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-8mpp-f3f7-xc28
- https://nvd.nist.gov/vuln/detail/CVE-2022-2191
- https://github.com/eclipse/jetty.project/issues/8161
- https://github.com/eclipse/jetty.project
- https://security.netapp.com/advisory/ntap-20220909-0003
