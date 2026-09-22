# [H] Important: kernel security and bug fix update

## Summary
Severity: High
Advisory: RXSA-2024:4211
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-15
Source: https://osv.dev/vulnerability/RXSA-2024:4211
Type: osv

## Details
The kernel packages contain the Linux kernel, the core of any Linux operating system.

Security Fix(es):

* kernel: Bluetooth BR/EDR PIN Pairing procedure is vulnerable to an impersonation attack (CVE-2020-26555)

* kernel: TCP-spoofed ghost ACKs and leak leak initial sequence number (CVE-2023-52881,RHV-2024-1001)

* kernel: ovl: fix leaked entry (CVE-2021-46972)

* kernel: platform/x86: dell-smbios-wmi: Fix oops on rmmod dell_smbios (CVE-2021-47073)

* kernel: gro: fix ownership transfer (CVE-2024-35890)

* kernel: tls: (CVE-2024-26584, CVE-2024-26583, CVE-2024-26585)

* kernel: wifi: (CVE-2024-35789, CVE-2024-27410, CVE-2024-35838, CVE-2024-35845)

* kernel: mlxsw: (CVE-2024-35855, CVE-2024-35854, CVE-2024-35853, CVE-2024-35852, CVE-2024-36007)

* kernel: PCI interrupt mapping cause oops [rhel-8] (CVE-2021-46909)

* kernel: ipc/mqueue, msg, sem: avoid relying on a stack reference past its expiry (CVE-2021-47069)

* kernel: hwrng: core - Fix page fault dead lock on mmap-ed hwrng [rhel-8] (CVE-2023-52615)

* kernel: net/mlx5e: (CVE-2023-52626, CVE-2024-35835, CVE-2023-52667, CVE-2024-35959)

* kernel: drm/amdgpu: use-after-free vulnerability (CVE-2024-26656)

* kernel: Bluetooth: Avoid potential use-after-free in hci_error_reset [rhel-8] (CVE-2024-26801)

* kernel: Squashfs: check the inode number is not the invalid value of zero (CVE-2024-26982)

* kernel: netfilter: nf_tables: use timestamp to check for set element timeout [rhel-8.10] (CVE-2024-27397)

* kernel: mm/damon/vaddr-test: memory leak in damon_do_test_apply_three_regions() (CVE-2023-52560)

* kernel: ppp_async: limit MRU to 64K (CVE-2024-26675)

* kernel: x86/mm/swap: (CVE-2024-26759, CVE-2024-26906)

* kernel: tipc: fix kernel warning when sending SYN message [rhel-8] (CVE-2023-52700)

* kernel: RDMA/mlx5: Fix fortify source warning while accessing Eth segment (CVE-2024-26907)

* kernel: erspan: make sure erspan_base_hdr is present in skb-&gt;head (CVE-2024-35888)

* kernel: powerpc/imc-pmu/powernv: (CVE-2023-52675, CVE-2023-52686)

* kernel: KVM: SVM: improper check in svm_set_x2apic_msr_interception allows direct access to host x2apic msrs (CVE-2023-5090)

* kernel: EDAC/thunderx: Incorrect buffer size in drivers/edac/thunderx_edac.c (CVE-2023-52464)

* kernel: ipv6: sr: fix possible use-after-free and null-ptr-deref (CVE-2024-26735)

* kernel: mptcp: fix data re-injection from stale subflow (CVE-2024-26826)

* kernel: crypto: (CVE-2024-26974, CVE-2023-52669, CVE-2023-52813)

* kernel: net/mlx5/bnx2x/usb: (CVE-2024-35960, CVE-2024-35958, CVE-2021-47310, CVE-2024-26804, CVE-2021-47311, CVE-2024-26859, CVE-2021-47236, CVE-2023-52703)

* kernel: i40e: Do not use WQ_MEM_RECLAIM flag for workqueue (CVE-2024-36004)

* kernel: perf/core: Bail out early if the request AUX area is out of bound (CVE-2023-52835)

* kernel: USB/usbnet: (CVE-2023-52781, CVE-2023-52877, CVE-2021-47495)

* kernel: can: (CVE-2023-52878, CVE-2021-47456)

* kernel: mISDN: fix possible use-after-free in HFC_cleanup() (CVE-2021-47356)

* kernel: udf: Fix NULL pointer dereference in udf_symlink function (CVE-2021-47353)

Bug Fix(es):

* Kernel panic - kernel BUG at mm/slub.c:376! (JIRA:Rocky Linux SIG Cloud-29783)

* Temporary values in FIPS integrity test should be zeroized [rhel-8.10.z] (JIRA:Rocky Linux SIG Cloud-35361)

* Rocky Linux SIG Cloud8.6 - kernel: s390/cpum_cf: make crypto counters upward compatible (JIRA:Rocky Linux SIG Cloud-36048)

* [Rocky Linux SIG Cloud8] blktests block/024 failed (JIRA:Rocky Linux SIG Cloud-8130)

* Rocky Linux SIG Cloud8.9: EEH injections results  Error:  Power fault on Port 0 and other call traces(Everest/1050/Shiner) (JIRA:Rocky Linux SIG Cloud-14195)

* Latency spikes with Matrox G200 graphic cards (JIRA:Rocky Linux SIG Cloud-36172)

For more details about the security issue(s), including the impact, a CVSS score, acknowledgments, and other related information, refer to the CVE page(s) listed in the References section.

## References
- https://errata.rockylinux.org/RXSA-2024:4211
- https://bugzilla.redhat.com/show_bug.cgi?id=1918601
- https://bugzilla.redhat.com/show_bug.cgi?id=2248122
- https://bugzilla.redhat.com/show_bug.cgi?id=2258875
- https://bugzilla.redhat.com/show_bug.cgi?id=2265517
- https://bugzilla.redhat.com/show_bug.cgi?id=2265519
- https://bugzilla.redhat.com/show_bug.cgi?id=2265520
- https://bugzilla.redhat.com/show_bug.cgi?id=2265800
- https://bugzilla.redhat.com/show_bug.cgi?id=2266408
- https://bugzilla.redhat.com/show_bug.cgi?id=2266831
- https://bugzilla.redhat.com/show_bug.cgi?id=2267513
- https://bugzilla.redhat.com/show_bug.cgi?id=2267518
- https://bugzilla.redhat.com/show_bug.cgi?id=2267730
- https://bugzilla.redhat.com/show_bug.cgi?id=2270093
- https://bugzilla.redhat.com/show_bug.cgi?id=2271680
- https://bugzilla.redhat.com/show_bug.cgi?id=2272692
- https://bugzilla.redhat.com/show_bug.cgi?id=2272829
- https://bugzilla.redhat.com/show_bug.cgi?id=2273204
- https://bugzilla.redhat.com/show_bug.cgi?id=2273278
- https://bugzilla.redhat.com/show_bug.cgi?id=2273423
