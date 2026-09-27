# [H] CVE-2018-19158

## Summary
Severity: High
Advisory: CVE-2018-19158
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-19158
Type: osv

## Details
ColossusCoinXT through 1.0.5 (a chain-based proof-of-stake cryptocurrency) allows a remote denial of service, exploitable by an attacker who acquires even a small amount of stake/coins in the system. The attacker sends invalid headers/blocks, which are stored on the victim's disk.

## References
- https://medium.com/%40dsl_uiuc/fake-stake-attacks-on-chain-based-proof-of-stake-cryptocurrencies-b8b05723f806
- http://fc19.ifca.ai/preproceedings/180-preproceedings.pdf
- https://github.com/ColossusCoinXT/ColossusCoinXT/compare/0223904...9666bb8
