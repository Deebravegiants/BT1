# [M] CVE-2025-14896

## Summary
Severity: Medium
Advisory: CVE-2025-14896
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-14896
Type: osv

## Details
due to insufficient sanitazation in Vega’s `convert()` function when `safeMode` is enabled and the spec variable is an array. An attacker can craft a malicious Vega diagram specification that will allow them to send requests to any URL, including local file system paths, leading to exposure of sensitive information.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14896.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14896
- https://github.com/yuzutech/kroki/commit/f31093cd8a0a1d6999c43d560f62d1e82d59c77e
