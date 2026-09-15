# [H] i40e: Fix call trace in setup_tx_descriptors

## Summary
Severity: High
Advisory: CVE-2022-49725
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49725
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.14.285, >=4.15.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: Fix call trace in setup_tx_descriptors

After PF reset and ethtool -t there was call trace in dmesg
sometimes leading to panic. When there was some time, around 5
seconds, between reset and test there were no errors.

Problem was that pf reset calls i40e_vsi_close in prep_for_reset
and ethtool -t calls i40e_vsi_close in diag_test. If there was not
enough time between those commands the second i40e_vsi_close starts
before previous i40e_vsi_close was done which leads to crash.

Add check to diag_test if pf is in reset and don't start offline
tests if it is true.
Add netif_info("testing failed") into unhappy path of i40e_diag_test()

## References
- https://git.kernel.org/stable/c/0a4e5a3dc5e41212870e6043895ae02455c93f63
- https://git.kernel.org/stable/c/15950157e2c24865b696db1c9ccc72743ae0e967
- https://git.kernel.org/stable/c/322271351b0e41565171e4cce70ea41854fac115
- https://git.kernel.org/stable/c/5ba9956ca57e361fb13ea369bb753eb33177acc7
- https://git.kernel.org/stable/c/814092927a215f5ca6c08249ec72a205e0b473cd
- https://git.kernel.org/stable/c/fd5855e6b1358e816710afee68a1d2bc685176ca
- https://git.kernel.org/stable/c/ff6e03fe84bc917bb0c907d02de668c2fe101712
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49725.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49725
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
