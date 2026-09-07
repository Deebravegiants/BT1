# [M] XSS in jQuery as used in Drupal, Backdrop CMS, and other products

## Summary
Severity: Medium
Advisory: GHSA-6c3j-c64m-qhgq
CVE: CVE-2019-11358
CWE: CWE-1321, CWE-79
Ecosystem: Maven, NuGet, Packagist, PyPI, RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-04-26
Source: https://github.com/advisories/GHSA-6c3j-c64m-qhgq
Type: github-advisory

## Affected
- npm: `jquery` — affected >=1.1.4 <3.4.0
- RubyGems: `jquery-rails` — affected >=0 <4.3.4
- NuGet: `jQuery` — affected >=1.1.4 <3.4.0
- PyPI: `django` — affected >=2.0a1 <2.1.9
- PyPI: `django` — affected >=2.2a1 <2.2.2
- Maven: `org.webjars.npm:jquery` — affected >=1.1.4 <3.4.0
- Packagist: `maximebf/debugbar` — affected >=0 <1.19.0

## Details
jQuery from 1.1.4 until 3.4.0, as used in Drupal, Backdrop CMS, and other products, mishandles `jQuery.extend(true, {}, ...)` because of `Object.prototype` pollution. If an unsanitized source object contained an enumerable `__proto__` property, it could extend the native `Object.prototype`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11358
- https://github.com/maximebf/php-debugbar/issues/447
- https://github.com/jquery/jquery/pull/4333
- https://github.com/maximebf/php-debugbar/commit/847216e60544258c881f2733d699bbcfeefac0fc
- https://github.com/django/django/commit/34ec52269ade54af31a021b12969913129571a3f
- https://github.com/django/django/commit/95649bc08547a878cebfa1d019edec8cb1b80829
- https://github.com/django/django/commit/baaf187a4e354bf3976c51e2c83a0d2f8ee6e6ad
- https://github.com/jquery/jquery/commit/753d591aea698e57d6db58c9f722cd0808619b1b
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WZW27UCJ5CYFL4KFFFMYMIBNMIU2ALG5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4UOAZIFCSZ3ENEFOR5IXX6NFAD3HV7FA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5IABSKTYZ5JUGL735UKGXL5YPRYOPUYI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KYH3OAGR2RTCHRA5NOKX2TES7SNQMWGO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QV3PKZC3PQCO3273HAT76PAQZFBEO4KP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RLXRX23725JL366CNZGJZ7AQQB7LHQ6F
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZW27UCJ5CYFL4KFFFMYMIBNMIU2ALG5
- https://seclists.org/bugtraq/2019/Apr/32
- https://seclists.org/bugtraq/2019/Jun/12
- https://seclists.org/bugtraq/2019/May/18
- https://www.tenable.com/security/tns-2020-02
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RLXRX23725JL366CNZGJZ7AQQB7LHQ6F
