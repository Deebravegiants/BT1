# [M] Requests has Insecure Temp File Reuse in its extract_zipped_paths() utility function

## Summary
Severity: Medium
Advisory: GHSA-gc5v-m9x4-r6x2
CVE: CVE-2026-25645
CWE: CWE-377
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-gc5v-m9x4-r6x2
Type: github-advisory

## Affected
- PyPI: `requests` — affected >=0 <2.33.0

## Details
### Impact
The `requests.utils.extract_zipped_paths()` utility function uses a predictable filename when extracting files from zip archives into the system temporary directory. If the target file already exists, it is reused without validation. A local attacker with write access to the temp directory could pre-create a malicious file that would be loaded in place of the legitimate one.

### Affected usages
**Standard usage of the Requests library is not affected by this vulnerability.** Only applications that call `extract_zipped_paths()` directly are impacted.

### Remediation
Upgrade to at least Requests 2.33.0, where the library now extracts files to a non-deterministic location.

If developers are unable to upgrade, they can set `TMPDIR` in their environment to a directory with restricted write access.

## References
- https://github.com/psf/requests/security/advisories/GHSA-gc5v-m9x4-r6x2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25645
- https://github.com/psf/requests/commit/66d21cb07bd6255b1280291c4fafb71803cdb3b7
- https://github.com/psf/requests
- https://github.com/psf/requests/releases/tag/v2.33.0
