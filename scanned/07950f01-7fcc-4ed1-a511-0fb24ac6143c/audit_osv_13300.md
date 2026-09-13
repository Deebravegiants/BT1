# [H] CVE-2018-19152

## Summary
Severity: High
Advisory: CVE-2018-19152
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-05
Source: https://osv.dev/vulnerability/CVE-2018-19152
Type: osv

## Details
emercoin through 0.7 (a chain-based proof-of-stake cryptocurrency) allows a remote denial of service. The attacker sends invalid headers/blocks. The attack requires no stake and can fill the victim's disk and RAM.

## References
- https://medium.com/%40dsl_uiuc/fake-stake-attacks-on-chain-based-proof-of-stake-cryptocurrencies-b8b05723f806
- http://fc19.ifca.ai/preproceedings/180-preproceedings.pdf
