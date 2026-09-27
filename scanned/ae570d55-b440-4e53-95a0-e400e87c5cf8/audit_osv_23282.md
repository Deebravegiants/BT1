# [H] CVE-2022-46836

## Summary
Severity: High
Advisory: CVE-2022-46836
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-46836
Type: osv

## Details
PHP code injection in watolib auth.php and hosttags.php in Tribe29's Checkmk <= 2.1.0p10, Checkmk <= 2.0.0p27, and Checkmk <= 1.6.0p29 allows an attacker to inject and execute PHP code which will be executed upon request of the vulnerable component.

## References
- https://checkmk.com/werk/14383
- https://www.sonarsource.com/blog/checkmk-rce-chain-3/
