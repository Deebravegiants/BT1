# [H] HTTP/2 HPACK integer overflow and buffer allocation

## Summary
Severity: High
Advisory: GHSA-wgh7-54f2-x98r
CVE: CVE-2023-36478
CWE: CWE-190
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-wgh7-54f2-x98r
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty.http2:http2-hpack` — affected >=10.0.0 <10.0.16
- Maven: `org.eclipse.jetty.http2:http2-hpack` — affected >=11.0.0 <11.0.16
- Maven: `org.eclipse.jetty.http3:http3-qpack` — affected >=10.0.0 <10.0.16
- Maven: `org.eclipse.jetty.http3:http3-qpack` — affected >=11.0.0 <11.0.16
- Maven: `org.eclipse.jetty.http2:http2-hpack` — affected >=9.3.0 <9.4.53

## Details
An integer overflow in `MetaDataBuilder.checkSize` allows for HTTP/2 HPACK header values to
exceed their size limit. 

In `MetaDataBuilder.java`, the following code determines if a header name or value
exceeds the size limit, and throws an exception if the limit is exceeded:

```java
291 public void checkSize(int length, boolean huffman) throws SessionException
292 {
293 // Apply a huffman fudge factor
294 if (huffman)
295 length = (length * 4) / 3;
296 if ((_size + length) > _maxSize)
297 throw new HpackException.SessionException("Header too large %d > %d",
_size + length, _maxSize);
298 }
```

However, when length is very large and huffman is true, the multiplication by 4 in line 295
will overflow, and length will become negative. (_size+length) will now be negative, and
the check on line 296 will not be triggered.

Furthermore, `MetaDataBuilder.checkSize` allows for user-entered HPACK header value sizes to be
negative, potentially leading to a very large buffer allocation later on when the
user-entered size is multiplied by 2.

In `MetaDataBuilder.java`, the following code determines if a header name or value
exceeds the size limit, and throws an exception if the limit is exceeded:

```java
public void checkSize(int length, boolean huffman) throws SessionException
{
// Apply a huffman fudge factor
if (huffman)
length = (length * 4) / 3;
if ((_size + length) > _maxSize)
throw new HpackException.SessionException("Header too large %d > %d", _size
+ length, _maxSize);
}
```

However, no exception is thrown in the case of a negative size.
Later, in `Huffman.decode`, the user-entered length is multiplied by 2 before allocating a buffer:

```java
public static String decode(ByteBuffer buffer, int length) throws
HpackException.CompressionException
{
Utf8StringBuilder utf8 = new Utf8StringBuilder(length * 2);
// ...
```

This means that if a user provides a negative length value (or, more precisely, a length
value which, when multiplied by the 4/3 fudge factor, is negative), and this length value is a
very large positive number when multiplied by 2, then the user can cause a very large
buffer to be allocated on the server.


### Exploit Scenario 1
An attacker repeatedly sends HTTP messages with the HPACK header 0x00ffffffffff02.
Each time this header is decoded:
+ `HpackDecode.decode` will determine that a Huffman-coded value of length
805306494 needs to be decoded.
+ `MetaDataBuilder.checkSize` will approve this length.
+ Huffman.decode will allocate a 1.6 GB string array.
+ Huffman.decode will have a buffer overflow error, and the array will be deallocated
the next time garbage collection happens. (Note: this can be delayed by appending
valid huffman-coded characters to the end of the header.)

Depending on the timing of garbage collection, the number of threads, and the amount of
memory available on the server, this may cause the server to run out of memory.


### Exploit Scenario 2
An attacker repeatedly sends HTTP messages with the HPACK header 0x00ff8080ffff0b. Each
time this header is decoded:
 + HpackDecode.decode will determine that a Huffman-coded value of length
-1073758081 needs to be decoded
 +  MetaDataBuilder.checkSize will approve this length
 + The number will be multiplied by 2 to get 2147451134, and Huffman.decode will
allocate a 2.1 GB string array
 + Huffman.decode will have a buffer overflow error, and the array will be deallocated
the next time garbage collection happens (Note that this deallocation can be
delayed by adding valid Huffman-coded characters to the end of the header)

Depending on the timing of garbage collection, the number of threads, and the amount of
memory available on the server, this may cause the server to run out of memory.

### Impact
Users of HTTP/2 can be impacted by a remote denial of service attack.

### Patches
Fixed in Jetty 10.0.16 and Jetty 11.0.16
Fixed in Jetty 9.4.53
Jetty 12.x is unaffected.

### Workarounds
No workarounds possible, only patched versions of Jetty.

### References
* https://github.com/eclipse/jetty.project/pull/9634

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-wgh7-54f2-x98r
- https://github.com/jetty/jetty.project/security/advisories/GHSA-wgh7-54f2-x98r
- https://nvd.nist.gov/vuln/detail/CVE-2023-36478
- https://github.com/eclipse/jetty.project/pull/9634
- https://github.com/eclipse/jetty.project
- https://github.com/eclipse/jetty.project/releases/tag/jetty-10.0.16
- https://github.com/eclipse/jetty.project/releases/tag/jetty-11.0.16
- https://github.com/eclipse/jetty.project/releases/tag/jetty-9.4.53.v20231009
- https://lists.debian.org/debian-lts-announce/2023/10/msg00045.html
- https://security.netapp.com/advisory/ntap-20231116-0011
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://www.debian.org/security/2023/dsa-5540
- http://www.openwall.com/lists/oss-security/2023/10/18/4
