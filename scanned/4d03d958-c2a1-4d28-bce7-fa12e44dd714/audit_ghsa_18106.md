# [C] internetarchive Vulnerable to Directory Traversal in File.download()

## Summary
Severity: Critical
Advisory: GHSA-wx3r-v6h7-frjp
CVE: CVE-2025-58438
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-09-05
Source: https://github.com/advisories/GHSA-wx3r-v6h7-frjp
Type: github-advisory

## Affected
- PyPI: `internetarchive` — affected >=0 <5.5.1

## Details
### Impact
**What kind of vulnerability is it?**
This is a **Critical** severity directory traversal (path traversal) vulnerability in the `File.download()` method of the `internetarchive` library.

**Who is impacted?**
All users of the `internetarchive` library versions `< 5.5.1` are impacted. The vulnerability is particularly critical for users on **Windows systems**, but all operating systems are affected.

**Description of the vulnerability:**
The vulnerability existed because the `file.download()` method did not properly sanitize user-supplied filenames or validate the final download path. A maliciously crafted filename could contain path traversal sequences (e.g., `../../../../windows/system32/file.txt`) or illegal characters that, when processed, would cause the file to be written outside of the intended target directory.

**Potential Impact:**
An attacker could potentially overwrite critical system files or application configuration files, leading to a denial of service, privilege escalation, or remote code execution, depending on the context in which the library is used.

### Patches
**Has the problem been patched?**
Yes, the problem has been patched.

**What versions should users upgrade to?**
Users must upgrade to version **5.5.1** or later.

### Workarounds
Is there a way for users to fix or remediate the vulnerability without upgrading?
There is no direct workaround that does not involve upgrading the library. The vulnerability is in the core logic of the file download process.

The only alternative for users who absolutely cannot upgrade is to implement their own custom download function that:

1. Manually sanitizes all filenames using a robust method.
2. Validates that the resolved absolute path of the download target is within the intended directory before writing any files.

However, this essentially re-implements the fix and is not recommended. Upgrading to the patched version is the only safe and supported solution.

### References

- [Release Notes for v5.5.1](https://github.com/jjjake/internetarchive/releases/tag/v5.5.1)
- [Commit with the fix](https://github.com/jjjake/internetarchive/commit/cba2d459e10a9489fb35caeba0b03e80f5f5d7c2)
- **CVE Identifier:**  CVE-2025-58438

## References
- https://github.com/jjjake/internetarchive/security/advisories/GHSA-wx3r-v6h7-frjp
- https://nvd.nist.gov/vuln/detail/CVE-2025-58438
- https://github.com/jjjake/internetarchive/commit/cba2d459e10a9489fb35caeba0b03e80f5f5d7c2
- https://github.com/jjjake/internetarchive
- https://github.com/jjjake/internetarchive/releases/tag/v5.5.1
- https://lists.debian.org/debian-lts-announce/2025/09/msg00030.html
