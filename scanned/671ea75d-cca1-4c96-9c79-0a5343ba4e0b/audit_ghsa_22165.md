# [H] bottle.py vulnerable to CRLF Injection

## Summary
Severity: High
Advisory: GHSA-j6f7-hghw-g437
CVE: CVE-2016-9964
CWE: CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j6f7-hghw-g437
Type: github-advisory

## Affected
- PyPI: `bottle` — affected >=0.10.1 <0.12.11

## Details
bottle.py is a fast and simple micro-framework for python web-applications. redirect() in bottle.py in bottle 0.12.10 doesn't filter a "\r\n" sequence, which leads to a CRLF attack, as demonstrated by a redirect("233\r\nSet-Cookie: name=salt") call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9964
- https://github.com/bottlepy/bottle/issues/913
- https://github.com/bottlepy/bottle/commit/6d7e13da0f998820800ecb3fe9ccee4189aefb54
- https://github.com/bottlepy/bottle/commit/78f67d51965db11cb1ed0003f1eb7926458b5c2c
- https://github.com/advisories/GHSA-j6f7-hghw-g437
- https://github.com/bottlepy/bottle
- https://github.com/pypa/advisory-database/tree/main/vulns/bottle/PYSEC-2016-24.yaml
- https://web.archive.org/web/20170214030628/http://www.securityfocus.com/bid/94961
- http://www.debian.org/security/2016/dsa-3743
