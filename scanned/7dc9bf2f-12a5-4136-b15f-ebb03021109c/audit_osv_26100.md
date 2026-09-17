# [H] CVE-2023-50981

## Summary
Severity: High
Advisory: CVE-2023-50981
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/CVE-2023-50981
Type: osv

## Details
ModularSquareRoot in Crypto++ (aka cryptopp) through 8.9.0 allows attackers to cause a denial of service (infinite loop) via crafted DER public-key data associated with squared odd numbers, such as the square of 268995137513890432434389773128616504853.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50981.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-50981
- https://github.com/weidai11/cryptopp/issues/1249
