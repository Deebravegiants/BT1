# [H] CVE-2022-4095

## Summary
Severity: High
Advisory: CVE-2022-4095
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-22
Source: https://osv.dev/vulnerability/CVE-2022-4095
Type: osv

## Details
A use-after-free flaw was found in Linux kernel before 5.19.2. This issue occurs in cmd_hdl_filter in drivers/staging/rtl8712/rtl8712_cmd.c, allowing an attacker to launch a local denial of service attack and gain escalation of privileges.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c53b3dcb9942b8ed7f81ee3921c4085d87070c73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4095.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4095
- https://security.netapp.com/advisory/ntap-20230420-0005/
