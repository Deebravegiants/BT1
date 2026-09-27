# [M] CVE-2020-11944

## Summary
Severity: Medium
Advisory: CVE-2020-11944
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-04-20
Source: https://osv.dev/vulnerability/CVE-2020-11944
Type: osv

## Details
Abe (aka bitcoin-abe) through 0.7.2, and 0.8pre, allows XSS in __call__ in abe.py because the PATH_INFO environment variable is mishandled during a PageNotFound exception.

## References
- https://geeknik-labs.com
- https://github.com/bitcoin-abe/bitcoin-abe/issues/292
- https://github.com/bitcoin-abe/bitcoin-abe/blob/d33f6e85de74e708e11cabe4ed0246e12025c726/Abe/abe.py#L253-L254
