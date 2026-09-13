# [H] CVE-2018-11548

## Summary
Severity: High
Advisory: CVE-2018-11548
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-29
Source: https://osv.dev/vulnerability/CVE-2018-11548
Type: osv

## Details
An issue was discovered in EOS.IO DAWN 4.2. plugins/net_plugin/net_plugin.cpp does not limit the number of P2P connections from the same source IP address.

## References
- https://github.com/EOSIO/eos/issues/3497
