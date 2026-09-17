# [M] FastGPT: DNS rebinding TOCTOU bypass in isInternalAddress allows SSRF on all protected endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-42344
Aliases: GHSA-cc8x-jrqv-hmwh
CVSS: 6.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42344
Type: osv

## Details
FastGPT is an AI Agent building platform. In versions 4.14.11 and prior, FastGPT's isInternalAddress() function in packages/service/common/system/utils.ts is vulnerable to DNS rebinding (TOCTOU — Time-of-Check to Time-of-Use). The function resolves the hostname via dns.resolve4()/dns.resolve6() and checks resolved IPs against private ranges, but the actual HTTP request happens in a separate call with a new DNS resolution, allowing the DNS record to change between validation and fetch. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42344.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-cc8x-jrqv-hmwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42344
