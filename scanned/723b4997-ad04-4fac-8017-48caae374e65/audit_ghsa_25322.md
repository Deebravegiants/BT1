# [M] Local Information Disclosure Vulnerability in io.netty:netty-codec-http

## Summary
Severity: Medium
Advisory: GHSA-269q-hmxg-m83q
CVE: CVE-2022-24823
CWE: CWE-378, CWE-379, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-10
Source: https://github.com/advisories/GHSA-269q-hmxg-m83q
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.77.Final

## Details
### Description ###
[GHSA-5mcr-gq6c-3hq2](https://github.com/netty/netty/security/advisories/GHSA-5mcr-gq6c-3hq2) (CVE-2021-21290) contains an insufficient fix for the vulnerability identified.

### Impact ###

When netty's multipart decoders are used local information disclosure can occur via the local system temporary directory if temporary storing uploads on the disk is enabled.

This only impacts applications running on Java version 6 and lower. Additionally, this vulnerability impacts code running on Unix-like systems, and very old versions of Mac OSX and Windows as they all share the system temporary directory between all users.

### Vulnerability Details ###

To fix the vulnerability the code was changed to the following:

```java
    @SuppressJava6Requirement(reason = "Guarded by version check")
    public static File createTempFile(String prefix, String suffix, File directory) throws IOException {
        if (javaVersion() >= 7) {
            if (directory == null) {
                return Files.createTempFile(prefix, suffix).toFile();
            }
            return Files.createTempFile(directory.toPath(), prefix, suffix).toFile();
        }
        if (directory == null) {
            return File.createTempFile(prefix, suffix);
        }
        File file = File.createTempFile(prefix, suffix, directory);
        // Try to adjust the perms, if this fails there is not much else we can do...
        file.setReadable(false, false);
        file.setReadable(true, true);
        return file;
    }
```

Unfortunately, this logic path was left vulnerable:

```java
        if (directory == null) {
            return File.createTempFile(prefix, suffix);
        }
```

This file is still readable by all local users.

### Patches ###

Update to 4.1.77.Final

### Workarounds ###

Specify your own `java.io.tmpdir` when you start the JVM or use `DefaultHttpDataFactory.setBaseDir(...)` to set the directory to something that is only readable by the current user or update to Java 7 or above.

### References ###

 - [CWE-378: Creation of Temporary File With Insecure Permissions](https://cwe.mitre.org/data/definitions/378.html)
 - [CWE-379: Creation of Temporary File in Directory with Insecure Permissions](https://cwe.mitre.org/data/definitions/379.html)


### For more information ###

If you have any questions or comments about this advisory:

Open an issue in [netty](https://github.com/netty/netty)

## References
- https://github.com/netty/netty/security/advisories/GHSA-269q-hmxg-m83q
- https://github.com/netty/netty/security/advisories/GHSA-5mcr-gq6c-3hq2
- https://nvd.nist.gov/vuln/detail/CVE-2022-24823
- https://github.com/netty/netty/commit/185f8b2756a36aaa4f973f1a2a025e7d981823f1
- https://github.com/netty/netty
- https://security.netapp.com/advisory/ntap-20220616-0004
- https://www.oracle.com/security-alerts/cpujul2022.html
