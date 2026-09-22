# [H] Arbitrary code execution in de.tum.in.ase:artemis-java-test-sandbox

## Summary
Severity: High
Advisory: GHSA-98hq-4wmw-98w9
CVE: CVE-2024-23681
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-98hq-4wmw-98w9
Type: github-advisory

## Affected
- Maven: `de.tum.in.ase:artemis-java-test-sandbox` — affected >=0 <1.11.2

## Details
### Summary
Because of the missing `checkLink(String)` override in the SecurityManager, students can load libraries and execute arbitrary code.

### Details
Using `System.load(String)` or `System.loadLibrary​(String)` students can load and execute arbitrary code.

```java
private static native void start(List<String> args);

public static void main(String[] args) {
  System.load(new File("path_to_lib.so").getAbsolutePath());
  start(List.of(args));
}
```

Adding this to the security manager (and a translation) should fix the issue:
```java
@Override
public void checkExec(String cmd) {
  try {
    if (enterPublicInterface())
      return;
    throw new SecurityException(localized("security.error_link")); //$NON-NLS-1$
  } finally {
    exitPublicInterface();
  }
}
```

### PoC
See details.

### Impact
Arbitrary code execution.

## References
- https://github.com/ls1intum/Ares/security/advisories/GHSA-98hq-4wmw-98w9
- https://nvd.nist.gov/vuln/detail/CVE-2024-23681
- https://github.com/ls1intum/Ares
- https://vulncheck.com/advisories/vc-advisory-GHSA-98hq-4wmw-98w9
