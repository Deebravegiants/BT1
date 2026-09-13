# [C] Command injection via array-ish $command parameter of proc_open()

## Summary
Severity: Critical
Advisory: BIT-libphp-2024-1874
Aliases: BIT-php-2024-1874, BIT-php-min-2024-1874, CVE-2024-1874, GHSA-pc52-254m-w9w7
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-1874
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.5

## Details
In PHP versions 8.1.* before 8.1.28, 8.2.* before 8.2.18, 8.3.* before 8.3.5, when using proc_open() command with array syntax, due to insufficient escaping, if the arguments of the executed command are controlled by a malicious user, the user can supply arguments that would execute arbitrary commands in Windows shell.

## References
- http://www.openwall.com/lists/oss-security/2024/04/12/11
- http://www.openwall.com/lists/oss-security/2024/06/07/1
- https://github.com/php/php-src/security/advisories/GHSA-pc52-254m-w9w7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PKGTQUOA2NTZ3RXN22CSAUJPIRUYRB4B/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W45DBOH56NQDRTOM2DN2LNA2FZIMC3PK/
- https://nvd.nist.gov/vuln/detail/CVE-2024-1874
- https://security.netapp.com/advisory/ntap-20240510-0009/
- https://www.vicarius.io/vsociety/posts/command-injection-vulnerability-in-php-on-windows-systems-cve-2024-1874-and-cve-2024-5585
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KJZK3X6B7FBE32FETDSMRLJXTFTHKWSY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGWIK3HMBACERGB4TSBB2JUOMPYY2VKY/
- https://www.kb.cert.org/vuls/id/123335
