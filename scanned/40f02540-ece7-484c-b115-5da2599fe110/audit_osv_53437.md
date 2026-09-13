# [M] CVE-2022-42432

## Summary
Severity: Medium
Advisory: CVE-2022-42432
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-29
Source: https://osv.dev/vulnerability/CVE-2022-42432
Type: osv

## Details
This vulnerability allows local attackers to disclose sensitive information on affected installations of the Linux Kernel 6.0-rc2. An attacker must first obtain the ability to execute high-privileged code on the target system in order to exploit this vulnerability. The specific flaw exists within the nft_osf_eval function. The issue results from the lack of proper initialization of memory prior to accessing it. An attacker can leverage this in conjunction with other vulnerabilities to execute arbitrary code in the context of the kernel. Was ZDI-CAN-18540.

## References
- https://patchwork.ozlabs.org/project/netfilter-devel/patch/20220907082618.1193201-1-pablo%40netfilter.org/
- https://www.zerodayinitiative.com/advisories/ZDI-22-1457/
