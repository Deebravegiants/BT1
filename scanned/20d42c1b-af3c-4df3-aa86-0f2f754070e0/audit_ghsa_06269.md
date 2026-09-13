# [H] Protego has exponential backtracking ReDoS in robots.txt URL wildcard matching

## Summary
Severity: High
Advisory: GHSA-wjmf-p669-5m5p
CVE: CVE-2026-55520
CWE: CWE-1333, CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-wjmf-p669-5m5p
Type: github-advisory

## Affected
- PyPI: `Protego` — affected >=0 <0.6.2

## Details
### Problem description

Protego constructs regular expressions to match URLs against `robots.txt` `Allow:` and `Disallow:` directives, see `protego._urlpattern._URLPattern._prepare_pattern_for_regex()`. Every `*` in the directive value is translated into a lazy `.*?` regex piece, thus a specially crafted directive value with many asterisks may produce a regex that freezes the parser due to exponential backtracking.

### Impact

Parsing a specially crafted `robots.txt` with `protego.Protego.parse()` and then trying to match an URL with `protego.Protego.can_fetch()` results in the latter call not returning for a period dependent on the length of the URL.

### Proof of concept

```python
from protego import Protego

robotstxt = f"""
User-agent: *
Disallow: /{"*1" * 12}*Z
"""
rp = Protego.parse(robotstxt)
url = "/" + "1" * 60
rp.can_fetch(url, "mybot")  # freezes
```

## References
- https://github.com/scrapy/protego/security/advisories/GHSA-wjmf-p669-5m5p
- https://github.com/scrapy/protego/commit/785940181659bf440ba82f1da148fade5087e858
- https://github.com/scrapy/protego
- https://github.com/scrapy/protego/releases/tag/0.6.2
