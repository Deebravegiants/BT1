# [H] CVE-2020-26947

## Summary
Severity: High
Advisory: CVE-2020-26947
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-10
Source: https://osv.dev/vulnerability/CVE-2020-26947
Type: osv

## Details
monero-wallet-gui in Monero GUI before 0.17.1.0 includes the . directory in an embedded RPATH (with a preference ahead of /usr/lib), which allows local users to gain privileges via a Trojan horse library in the current working directory.

## References
- https://github.com/monero-project/monero-gui/issues/3142#issuecomment-705940446
- https://github.com/monero-project/monero-gui/commit/6ed536982953d870010d8fa065dccbffeb6cae50
