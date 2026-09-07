# [H] Command injection in librenms

## Summary
Severity: High
Advisory: GHSA-23f2-vgr6-fwv7
CVE: CVE-2022-29712
CWE: CWE-74
Ecosystem: Packagist
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-23f2-vgr6-fwv7
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <22.4.0

## Details
LibreNMS v22.3.0 was discovered to contain multiple command injection vulnerabilities via the service_ip, hostname, and service_param parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29712
- https://github.com/librenms/librenms/pull/13932
- https://github.com/librenms/librenms/commit/8b82341cb742e7bd4966964b399012f7ba017e0b
- https://github.com/librenms/librenms
