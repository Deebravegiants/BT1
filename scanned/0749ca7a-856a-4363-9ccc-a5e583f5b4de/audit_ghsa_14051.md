# [H] Rekor's compressed archives can result in OOM conditions

## Summary
Severity: High
Advisory: GHSA-2h5h-59f5-c5x9
CVE: CVE-2023-30551
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-03
Source: https://github.com/advisories/GHSA-2h5h-59f5-c5x9
Type: github-advisory

## Affected
- Go: `github.com/sigstore/rekor` — affected >=0 <1.1.1

## Details
## Summary
Two vulnerabilities have been found in Rekor types for archive files JARs and APKs, where Rekor would crash due to out of memory conditions caused by reading archive metadata files into memory without checking their sizes first causing a Denial of Service of Rekor.

These vulnerabilities were found through fuzzing with [OSS-Fuzz](https://google.github.io/oss-fuzz/).

## Vulnerability 1: OOM due to large files in META-INF directory of JAR files.
### Summary
Verification of a JAR file submitted to Rekor can cause an out of memory crash if files within the META-INF directory of the JAR are sufficiently large.

### Details
As part of verifying a JAR file, Rekor uses the [relic library](http://github.com/sassoftware/relic) to check that the JAR is signed, the signature verifies, and that the hashes in the signed manifest are all valid. This library function reads files within META-INF/ into memory without checking their sizes, resulting in an OOM if the uncompressed file is sufficiently large. Rekor is also not performing any such checks prior to passing the JAR to this library function.

### Patches
Users should update to the latest version of Rekor, 1.1.1.

### Workaround
There are no workarounds, users should update.

## Vulnerability 2: OOM due to large .SIGN and .PKGINFO files in APK files.
### Summary
Parsing of an APK file submitted to Rekor can cause an out of memory crash if the .SIGN or .PKGINFO files within the APK are sufficiently large.

### Details
When parsing an APK file, Rekor allocates byte slices to read both the .SIGN and .PKGINFO files into memory in order to verify the signature and hashes in the APK. These byte slices are allocated based on the size included in the tar header for each file, with no checks performed on that size. If the size in the header is sufficiently large, either because the uncompressed file is large or the size in the header has been artificially set to a large value, Rekor will crash due to an out of memory panic.

### Patches
Users should update to the latest version of Rekor, 1.1.1.

### Workaround
There are no workarounds, users should update.

## References
- https://github.com/sigstore/rekor/security/advisories/GHSA-2h5h-59f5-c5x9
- https://nvd.nist.gov/vuln/detail/CVE-2023-30551
- https://github.com/sigstore/rekor/commit/cf42ace82667025fe128f7a50cf6b4cdff51cc48
- https://github.com/sigstore/rekor
- https://github.com/sigstore/rekor/releases/tag/v1.1.1
