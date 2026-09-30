# [M] CVE-2019-15302

## Summary
Severity: Medium
Advisory: CVE-2019-15302
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-09-11
Source: https://osv.dev/vulnerability/CVE-2019-15302
Type: osv

## Details
The pad management logic in XWiki labs CryptPad before 3.0.0 allows a remote attacker (who has access to a Rich Text pad with editing rights for the URL) to corrupt it (i.e., cause data loss) via a trivial URL modification.

## References
- https://github.com/xwiki-labs/cryptpad/releases/tag/3.0.0
- https://github.com/xwiki-labs/cryptpad/commits/staging
