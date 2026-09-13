# [C] Stack-Buffer Overflow in 'Call-ID' and 'X-Call-ID' SIP Header Processing in sngrep

## Summary
Severity: Critical
Advisory: CVE-2024-3119
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-04-09
Source: https://osv.dev/vulnerability/CVE-2024-3119
Type: osv

## Details
A buffer overflow vulnerability exists in all versions of sngrep since v0.4.2, due to improper handling of 'Call-ID' and 'X-Call-ID' SIP headers. The functions sip_get_callid and sip_get_xcallid in sip.c use the strncpy function to copy header contents into fixed-size buffers without checking the data length. This flaw allows remote attackers to execute arbitrary code or cause a denial of service (DoS) through specially crafted SIP messages.

## References
- https://github.com/irontec/sngrep/pull/480/commits/73c15c82d14c69df311e05fa75da734faafd365f
- https://github.com/irontec/sngrep/releases/tag/v1.8.1
- https://pentraze.com/vulnerability-reports/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3119.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3119
