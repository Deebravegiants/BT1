# [H] wolfSSL: out-of-bounds read (DoS) in ALPN parsing due to incomplete validation

## Summary
Severity: High
Advisory: CVE-2026-3547
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-3547
Type: osv

## Details
Out-of-bounds read in ALPN parsing due to incomplete validation. wolfSSL 5.8.4 and earlier contained an out-of-bounds read in ALPN handling when built with ALPN enabled (HAVE_ALPN / --enable-alpn). A crafted ALPN protocol list could trigger an out-of-bounds read, leading to a potential process crash (denial of service). Note that ALPN is disabled by default, but is enabled for these 3rd party compatibility features: enable-apachehttpd, enable-bind, enable-curl, enable-haproxy, enable-hitch, enable-lighty, enable-jni, enable-nginx, enable-quic.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3547.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3547
- https://github.com/wolfSSL/wolfssl/pull/9859
