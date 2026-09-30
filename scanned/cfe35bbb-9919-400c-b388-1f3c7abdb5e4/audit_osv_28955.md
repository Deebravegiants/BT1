# [H] Tencent RapidJSON include/rapidjson/reader.h GenericReader::ParseNumber() Function Template Exponent Parsing Integer Underflow

## Summary
Severity: High
Advisory: CVE-2024-38517
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H/E:U/RL:O/RC:C)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-38517
Type: osv

## Details
Tencent RapidJSON is vulnerable to privilege escalation due to an integer underflow in the `GenericReader::ParseNumber()` function of `include/rapidjson/reader.h` when parsing JSON text from a stream. An attacker needs to send the victim a crafted file which needs to be opened; this triggers the integer underflow vulnerability (when the file is parsed), leading to elevation of privilege.

## References
- https://github.com/Tencent/rapidjson/pull/1261/commits/8269bc2bc289e9d343bae51cdf6d23ef0950e001
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-38517
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38517.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38517
- https://security.netapp.com/advisory/ntap-20240905-0001/
- https://github.com/fmalita/rapidjson/commit/8269bc2bc289e9d343bae51cdf6d23ef0950e001
