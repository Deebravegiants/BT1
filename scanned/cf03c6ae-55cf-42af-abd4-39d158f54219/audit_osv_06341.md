# [M] Configuration Injection via Carriage Return (\r) in write() method

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-0864
Aliases: BIT-python-2026-0864, BIT-python-min-2026-0864, CVE-2026-0864, PSF-2026-29
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-libpython-2026-0864
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.7

## Details
When using the "configparser" module to write configuration files
containing multi-line text values with carriage return characters (\r) the
resulting file could be injected with unexpected keys and values if the
attacker controls the written value.

## References
- https://github.com/python/cpython/commit/0adb386f6e68eb2e73d32e19f235d012df009528
- https://github.com/python/cpython/commit/5858e42c539dac8394636a6e9b30472b8994851f
- https://github.com/python/cpython/commit/71f2e02a52d47417a6fd69f456346cd8aa7aca98
- https://github.com/python/cpython/commit/aaf850fd333cd89e9aada03d92aaa788a6cb1bb8
- https://github.com/python/cpython/issues/143927
- https://github.com/python/cpython/pull/151559
- https://mail.python.org/archives/list/security-announce@python.org/thread/CV4NE6AFCRJL7XQOHX7J5TSDHUWVWGJS/
- https://nvd.nist.gov/vuln/detail/CVE-2026-0864
- https://github.com/python/cpython/commit/12dcbd74d3563016a8cb8c47e4898889f34f74dd
- https://github.com/python/cpython/commit/274de100bbf4345bd0c23ef5b446722e9e636908
- https://github.com/python/cpython/commit/db4a157c790479710a1a840d7937c5c815a6f8b6
