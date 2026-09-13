# [C] IgnoreIP/IgnoreCIDR should not trust X-Forwarded-For

## Summary
Severity: Critical
Advisory: CVE-2023-45132
Aliases: GHSA-7qjc-q4j9-pc8x
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-10-11
Source: https://osv.dev/vulnerability/CVE-2023-45132
Type: osv

## Details
NAXSI is an open-source maintenance web application firewall (WAF) for NGINX. An issue present starting in version 1.3 and prior to version 1.6 allows someone to bypass the WAF when a malicious `X-Forwarded-For` IP matches `IgnoreIP` `IgnoreCIDR` rules. This old code was arranged to allow older NGINX versions to also support `IgnoreIP` `IgnoreCIDR` when multiple reverse proxies were present. The issue is patched in version 1.6. As a workaround, do not set any `IgnoreIP` `IgnoreCIDR` for older versions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45132.json
- https://github.com/wargio/naxsi/security/advisories/GHSA-7qjc-q4j9-pc8x
- https://nvd.nist.gov/vuln/detail/CVE-2023-45132
- https://github.com/wargio/naxsi/commit/1b712526ed3314dd6be7e8b0259eabda63c19537
- https://github.com/wargio/naxsi/pull/103
