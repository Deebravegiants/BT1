# [M] CVE-2020-13131

## Summary
Severity: Medium
Advisory: CVE-2020-13131
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-13131
Type: osv

## Details
An issue was discovered in Yubico libykpiv before 2.1.0. lib/util.c in this library (which is included in yubico-piv-tool) does not properly check embedded length fields during device communication. A malicious PIV token can misreport the returned length fields during RSA key generation. This will cause stack memory to be copied into heap allocated memory that gets returned to the caller. The leaked memory could include PINs, passwords, key material, and other sensitive information depending on the integration. During further processing by the caller, this information could leak across trust boundaries. Note that RSA key generation is triggered by the host and cannot directly be triggered by the token.

## References
- https://www.yubico.com/products/services-software/download/smart-card-drivers-tools/
- https://blog.inhq.net/posts/yubico-libykpiv-vuln/
