# [H] CVE-2018-19162

## Summary
Severity: High
Advisory: CVE-2018-19162
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-05
Source: https://osv.dev/vulnerability/CVE-2018-19162
Type: osv

## Details
Divi through 4.0.5 (a chain-based proof-of-stake cryptocurrency) allows a remote denial of service, exploitable by an attacker who acquires even a small amount of stake/coins in the system. The attacker sends invalid headers/blocks, which are stored on the victim's disk.

## References
- https://medium.com/%40dsl_uiuc/fake-stake-attacks-on-chain-based-proof-of-stake-cryptocurrencies-b8b05723f806
- http://fc19.ifca.ai/preproceedings/180-preproceedings.pdf
