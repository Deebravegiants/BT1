# [H] CVE-2021-20268

## Summary
Severity: High
Advisory: CVE-2021-20268
Aliases: A-182986620, PUB-A-182986620
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2021-20268
Type: osv

## Details
An out-of-bounds access flaw was found in the Linux kernel's implementation of the eBPF code verifier in the way a user running the eBPF script calls dev_map_init_map or sock_map_alloc. This flaw allows a local user to crash the system or possibly escalate their privileges. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://lore.kernel.org/bpf/CACAyw99bEYWJCSGqfLiJ9Jp5YE1ZsZSiJxb4RFUTwbofipf0dA%40mail.gmail.com/T/#m8929643e99bea9c18ed490a7bc2591145eac6444
- https://security.netapp.com/advisory/ntap-20210409-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1923816
