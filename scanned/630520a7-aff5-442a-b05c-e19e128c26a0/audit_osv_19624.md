# [H] CVE-2021-22948

## Summary
Severity: High
Advisory: CVE-2021-22948
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2021-09-23
Source: https://osv.dev/vulnerability/CVE-2021-22948
Type: osv

## Details
Vulnerability in the generation of session IDs in revive-adserver < 5.3.0, based on the cryptographically insecure uniqid() PHP function. Under some circumstances, an attacker could theoretically be able to brute force session IDs in order to take over a specific account.

## References
- https://www.revive-adserver.com/security/revive-sa-2021-005/
- https://hackerone.com/reports/1187820
