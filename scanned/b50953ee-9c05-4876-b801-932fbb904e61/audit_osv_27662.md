# [M] `ZipSecurity#isBelowCurrentDirectory` is vulnerable to partial-path traversal vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-24569
Aliases: GHSA-qh4g-4m4w-jgv2
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2024-02-01
Source: https://osv.dev/vulnerability/CVE-2024-24569
Type: osv

## Details
The Pixee Java Code Security Toolkit is a set of security APIs meant to help secure Java code. `ZipSecurity#isBelowCurrentDirectory` is vulnerable to a partial-path traversal bypass. To be vulnerable to the bypass, the application must use toolkit version <=1.1.1, use ZipSecurity as a guard against path traversal, and have an exploit path. Although the control still protects attackers from escaping the application path into higher level directories (e.g., /etc/), it will allow "escaping" into sibling paths. For example, if your running path is /my/app/path you an attacker could navigate into /my/app/path-something-else. This vulnerability is patched in 1.1.2.

## References
- https://github.com/pixee/java-security-toolkit/blob/7c8e93e6fb2420fb6003c54a741e267c4f883bab/src/main/java/io/github/pixee/security/ZipSecurity.java#L82-L87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24569.json
- https://github.com/pixee/java-security-toolkit/security/advisories/GHSA-qh4g-4m4w-jgv2
- https://nvd.nist.gov/vuln/detail/CVE-2024-24569
- https://github.com/pixee/java-security-toolkit/commit/b885b03c9cfae53d62d239037f9654d973dd54d9
