# [H] CVE-2022-47909

## Summary
Severity: High
Advisory: CVE-2022-47909
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-47909
Type: osv

## Details
Livestatus Query Language (LQL) injection in the AuthUser HTTP query header of Tribe29's Checkmk <= 2.1.0p11, Checkmk <= 2.0.0p28, and all versions of Checkmk 1.6.0 (EOL) allows an attacker to perform direct queries to the application's core from localhost.

## References
- https://checkmk.com/werk/14384
- https://www.sonarsource.com/blog/checkmk-rce-chain-1/
