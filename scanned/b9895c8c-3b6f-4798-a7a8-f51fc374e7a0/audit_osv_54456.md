# [H] CVE-2023-6546

## Summary
Severity: High
Advisory: CVE-2023-6546
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-21
Source: https://osv.dev/vulnerability/CVE-2023-6546
Type: osv

## Details
A race condition was found in the GSM 0710 tty multiplexor in the Linux kernel. This issue occurs when two threads execute the GSMIOC_SETCONF ioctl on the same tty file descriptor with the gsm line discipline enabled, and can lead to a use-after-free problem on a struct gsm_dlci while restarting the gsm mux. This could allow a local unprivileged user to escalate their privileges on the system.

## References
- http://www.openwall.com/lists/oss-security/2024/04/10/21
- http://www.openwall.com/lists/oss-security/2024/04/16/2
- http://www.openwall.com/lists/oss-security/2024/04/17/1
- http://www.openwall.com/lists/oss-security/2024/04/11/9
- http://www.openwall.com/lists/oss-security/2024/04/12/1
- http://www.openwall.com/lists/oss-security/2024/04/12/2
- http://www.openwall.com/lists/oss-security/2024/04/11/7
- http://www.openwall.com/lists/oss-security/2024/04/10/18
- https://access.redhat.com/errata/RHSA-2024:1612
- https://access.redhat.com/errata/RHSA-2024:4729
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-20527
- https://access.redhat.com/errata/RHSA-2024:1607
- https://access.redhat.com/errata/RHSA-2024:1614
- https://access.redhat.com/security/cve/CVE-2023-6546
- https://access.redhat.com/errata/RHSA-2024:0937
- https://access.redhat.com/errata/RHSA-2024:1253
- https://access.redhat.com/errata/RHSA-2024:2621
- https://access.redhat.com/errata/RHSA-2024:4577
- https://access.redhat.com/errata/RHSA-2024:1018
- https://access.redhat.com/errata/RHSA-2024:1019
