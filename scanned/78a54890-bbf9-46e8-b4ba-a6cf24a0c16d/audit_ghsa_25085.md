# [M] Symfony Vulnerable to PHP Eval Injection

## Summary
Severity: Medium
Advisory: GHSA-5c58-w9xc-qcj9
CVE: CVE-2015-2308
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5c58-w9xc-qcj9
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.3.27
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.5.11
- Packagist: `symfony/symfony` — affected >=2.6.0 <2.6.6
- Packagist: `symfony/http-kernel` — affected >=2.0.0 <2.3.27
- Packagist: `symfony/http-kernel` — affected >=2.4.0 <2.5.11
- Packagist: `symfony/http-kernel` — affected >=2.6.0 <2.6.6

## Details
Applications with ESI support (and SSI support as of Symfony 2.6) enabled and using the Symfony built-in reverse proxy (the `Symfony\Component\HttpKernel\HttpCache class) are vulnerable to PHP code injection; a malicious user can inject PHP code that will be executed by the server.

HttpCache uses eval() to execute files in its cache when they contain ESI tags (and only when ESI is enabled). The vulnerability comes from the fact that PHP allows contents of <script language="php"> tags to be executed (and this kind of PHP tags is always available regardless of the configuration), but there were not escaped before the evaluation.

A possible exploit comes from websites also vulnerable to Cross-Site Scripting as an attacker can successfully conduct a PHP code injection attack by passing such a tag in a user submitted variable (for which proper output escaping was not applied).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2308
- https://github.com/symfony/symfony/pull/14167/commits/195c57e1f50765aff33137689b16e126a689056a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-kernel/CVE-2015-2308.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2015-2308.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2015-2308-esi-code-injection
- https://symfony.com/cve-2015-2308
- https://web.archive.org/web/20200228084751/http://www.securityfocus.com/bid/75357
- http://jvn.jp/en/jp/JVN19578958/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2015-000089
