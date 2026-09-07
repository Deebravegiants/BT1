# [M] Guava vulnerable to insecure use of temporary directory

## Summary
Severity: Medium
Advisory: GHSA-7g45-4rm6-3mm3
CVE: CVE-2023-2976
CWE: CWE-379, CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-7g45-4rm6-3mm3
Type: github-advisory

## Affected
- Maven: `com.google.guava:guava` — affected >=1.0 <32.0.0-android

## Details
Use of Java's default temporary directory for file creation in `FileBackedOutputStream` in Google Guava versions 1.0 to 31.1 on Unix systems and Android Ice Cream Sandwich allows other users and apps on the machine with access to the default Java temporary directory to be able to access the files created by the class.

Even though the security vulnerability is fixed in version 32.0.0, maintainers recommend using version 32.0.1 as version 32.0.0 breaks some functionality under Windows.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2976
- https://github.com/google/guava/issues/2575
- https://github.com/google/guava/issues/6532
- https://github.com/google/guava/commit/feb83a1c8fd2e7670b244d5afd23cba5aca43284
- https://github.com/google/guava
- https://github.com/google/guava/releases/tag/v32.0.0
- https://security.netapp.com/advisory/ntap-20230818-0008
- https://security.netapp.com/advisory/ntap-20241108-0002
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-01006.html
