# [H] NuProcess vulnerable to command-line injection through insertion of NUL character(s)

## Summary
Severity: High
Advisory: GHSA-cxgf-v2p8-7ph7
CVE: CVE-2022-39243
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-cxgf-v2p8-7ph7
Type: github-advisory

## Affected
- Maven: `com.zaxxer:nuprocess` — affected >=1.2.0 <2.0.5

## Details
### Impact
In all the versions of NuProcess where it forks processes by using the JVM's Java_java_lang_UNIXProcess_forkAndExec method (1.2.0+), attackers can use NUL characters in their strings to perform command line injection. Java's ProcessBuilder isn't vulnerable because of a check in ProcessBuilder.start. NuProcess is missing that check.

This vulnerability can only be exploited to inject command line arguments on Linux.
- On macOS, any argument with a NUL character is truncated at that character. This means the malicious arguments are never seen by the started process.
- On Windows, the entire command line is truncated at the first NUL character. This means the malicious arguments, and any intentional arguments provided after them, are never seen by the started process.

### Patches
2.0.5

### Workarounds
Users of the library can sanitize command strings to remove NUL characters prior to passing them to NuProcess for execution.

### References
None.

## References
- https://github.com/brettwooldridge/NuProcess/security/advisories/GHSA-cxgf-v2p8-7ph7
- https://nvd.nist.gov/vuln/detail/CVE-2022-39243
- https://github.com/brettwooldridge/NuProcess/pull/143
- https://github.com/brettwooldridge/NuProcess/commit/29bc09de561bf00ff9bf77123756363a9709f868
- https://github.com/brettwooldridge/NuProcess
