# [H] FastGPT: Cloud metadata endpoint SSRF protection bypass via port specification, IPv6 mapping, hex/decimal IP encoding, and trailing dot

## Summary
Severity: High
Advisory: CVE-2026-42345
Aliases: GHSA-jhqw-944x-xh94
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42345
Type: osv

## Details
FastGPT is an AI Agent building platform. In versions 4.14.11 and prior, FastGPT's isInternalAddress() function in packages/service/common/system/utils.ts blocks cloud metadata endpoints using a fullUrl.startsWith() check against a hardcoded list. This check can be bypassed using at least 7 different URL encoding techniques, all of which resolve to the same cloud metadata service but do not match the blocklist patterns. Additionally, the broader private IP check (isInternalIPv4/isInternalIPv6) is disabled by default because CHECK_INTERNAL_IP defaults to false (not 'true'), so these bypasses reach the metadata endpoint without any further validation. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42345.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-jhqw-944x-xh94
- https://nvd.nist.gov/vuln/detail/CVE-2026-42345
