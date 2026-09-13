# [H] CVE-2024-25407

## Summary
Severity: High
Advisory: CVE-2024-25407
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/CVE-2024-25407
Type: osv

## Details
SteVe v3.6.0 was discovered to use predictable transaction ID's when receiving a StartTransaction request. This vulnerability can allow attackers to cause a Denial of Service (DoS) by using the predicted transaction ID's to terminate other transactions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25407.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25407
- https://github.com/steve-community/steve/issues/1296
