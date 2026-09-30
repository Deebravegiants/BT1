# [H] CVE-2021-20194

## Summary
Severity: High
Advisory: CVE-2021-20194
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-20194
Type: osv

## Details
There is a vulnerability in the linux kernel versions higher than 5.2 (if kernel compiled with config params CONFIG_BPF_SYSCALL=y , CONFIG_BPF=y , CONFIG_CGROUPS=y , CONFIG_CGROUP_BPF=y , CONFIG_HARDENED_USERCOPY not set, and BPF hook to getsockopt is registered). As result of BPF execution, the local user can trigger bug in __cgroup_bpf_run_filter_getsockopt() function that can lead to heap overflow (because of non-hardened usercopy). The impact of attack could be deny of service or possibly privileges escalation.

## References
- https://security.netapp.com/advisory/ntap-20210326-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1912683
