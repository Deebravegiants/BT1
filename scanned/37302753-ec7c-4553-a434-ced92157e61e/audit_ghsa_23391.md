# [H] Django Vulnerable to HTTP Response Splitting Attack

## Summary
Severity: High
Advisory: GHSA-q5qw-4364-5hhm
CVE: CVE-2015-5144
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q5qw-4364-5hhm
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.21
- PyPI: `Django` — affected >=1.5 <1.7.9
- PyPI: `Django` — affected >=1.8a1 <1.8.3

## Details
Django before 1.4.21, 1.5.x through 1.6.x, 1.7.x before 1.7.9, and 1.8.x before 1.8.3 uses an incorrect regular expression, which allows remote attackers to inject arbitrary headers and conduct HTTP response splitting attacks via a newline character in an (1) email message to the EmailValidator, a (2) URL to the URLValidator, or unspecified vectors to the (3) validate_ipv4_address or (4) validate_slug validator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5144
- https://github.com/django/django/commit/1ba1cdce7d58e6740fe51955d945b56ae51d072a
- https://github.com/django/django/commit/574dd5e0b0fbb877ae5827b1603d298edc9bb2a0
- https://github.com/django/django/commit/8f9a4d3a2bc42f14bb437defd30c7315adbff22c
- https://github.com/django/django/commit/ae49b4d994656bc037513dcd064cb9ce5bb85649
- https://github.com/django/django
- https://github.com/django/django/blob/4555a823fd57e261e1b19c778429473256c8ea08/docs/releases/1.4.21.txt#L30-L54
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-10.yaml
- https://security.gentoo.org/glsa/201510-06
- https://web.archive.org/web/20150924150801/http://www.securitytracker.com/id/1032820
- https://web.archive.org/web/20200228050526/http://www.securityfocus.com/bid/75665
- https://www.djangoproject.com/weblog/2015/jul/08/security-releases
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/172084.html
- http://lists.opensuse.org/opensuse-updates/2015-10/msg00043.html
- http://lists.opensuse.org/opensuse-updates/2015-10/msg00046.html
- http://www.debian.org/security/2015/dsa-3305
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
- http://www.ubuntu.com/usn/USN-2671-1
