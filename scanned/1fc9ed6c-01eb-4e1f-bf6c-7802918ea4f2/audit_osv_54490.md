# [M] CVE-2023-7042

## Summary
Severity: Medium
Advisory: CVE-2023-7042
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-21
Source: https://osv.dev/vulnerability/CVE-2023-7042
Type: osv

## Details
A null pointer dereference vulnerability was found in ath10k_wmi_tlv_op_pull_mgmt_tx_compl_ev() in drivers/net/wireless/ath/ath10k/wmi-tlv.c in the Linux kernel. This issue could be exploited to trigger a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-7042
- https://bugzilla.redhat.com/show_bug.cgi?id=2255497
- https://patchwork.kernel.org/project/linux-wireless/patch/20231208043433.271449-1-hdthky0@gmail.com/
- https://bugzilla.redhat.com/show_bug.cgi?id=2255497
- https://patchwork.kernel.org/project/linux-wireless/patch/20231208043433.271449-1-hdthky0@gmail.com/
- https://bugzilla.redhat.com/show_bug.cgi?id=2255497
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/54PLF5J33IRSLSR4UU6LQSMXX6FI5AOQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/C25BK2YH5MZ6VNQXKF2NAJBTGXVEPKGC/
