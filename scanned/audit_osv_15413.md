# [H] CVE-2019-15947

## Summary
Severity: High
Advisory: CVE-2019-15947
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-05
Source: https://osv.dev/vulnerability/CVE-2019-15947
Type: osv

## Details
In Bitcoin Core 0.18.0, bitcoin-qt stores wallet.dat data unencrypted in memory. Upon a crash, it may dump a core file. If a user were to mishandle a core file, an attacker can reconstruct the user's wallet.dat file, including their private keys, via a grep "6231 0500" command.

## References
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures#CVE-2019-15947
- https://gist.github.com/oxagast/50a121b2df32186e0c48411859d5861b
- https://security.gentoo.org/glsa/202009-18
- https://github.com/bitcoin/bitcoin/issues/16824
