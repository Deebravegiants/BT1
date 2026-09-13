# [C] Argument Injection in PHP-CGI

## Summary
Severity: Critical
Advisory: BIT-libphp-2024-4577
Aliases: BIT-php-2024-4577, BIT-php-min-2024-4577, CVE-2024-4577, GHSA-3qgc-jrrr-25jv
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-4577
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.8

## Details
In PHP versions 8.1.* before 8.1.29, 8.2.* before 8.2.20, 8.3.* before 8.3.8, when using Apache and PHP-CGI on Windows, if the system is set up to use certain code pages, Windows may use "Best-Fit" behavior to replace characters in command line given to Win32 API functions. PHP CGI module may misinterpret those characters as PHP options, which may allow a malicious user to pass options to PHP binary being run, and thus reveal the source code of scripts, run arbitrary PHP code on the server, etc.

## References
- http://www.openwall.com/lists/oss-security/2024/06/07/1
- https://arstechnica.com/security/2024/06/php-vulnerability-allows-attackers-to-run-malicious-code-on-windows-servers/
- https://blog.orange.tw/2024/06/cve-2024-4577-yet-another-php-rce.html
- https://blog.talosintelligence.com/new-persistent-attacks-japan/
- https://cert.be/en/advisory/warning-php-remote-code-execution-patch-immediately
- https://devco.re/blog/2024/06/06/security-alert-cve-2024-4577-php-cgi-argument-injection-vulnerability-en/
- https://github.com/11whoami99/CVE-2024-4577
- https://github.com/php/php-src/security/advisories/GHSA-3qgc-jrrr-25jv
- https://github.com/rapid7/metasploit-framework/pull/19247
- https://github.com/watchtowrlabs/CVE-2024-4577
- https://github.com/xcanwin/CVE-2024-4577-PHP-RCE
- https://isc.sans.edu/diary/30994
- https://labs.watchtowr.com/no-way-php-strikes-again-cve-2024-4577/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PKGTQUOA2NTZ3RXN22CSAUJPIRUYRB4B/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W45DBOH56NQDRTOM2DN2LNA2FZIMC3PK/
- https://nvd.nist.gov/vuln/detail/CVE-2024-4577
- https://security.netapp.com/advisory/ntap-20240621-0008/
- https://www.imperva.com/blog/imperva-protects-against-critical-php-vulnerability-cve-2024-4577/
- https://www.php.net/ChangeLog-8.php#8.1.29
- https://www.php.net/ChangeLog-8.php#8.2.20
