# [H] Use-after-free in Linux kernel's Performance Events subsystem

## Summary
Severity: High
Advisory: CVE-2023-2235
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-01
Source: https://osv.dev/vulnerability/CVE-2023-2235
Type: osv

## Details
A use-after-free vulnerability in the Linux Kernel Performance Events system can be exploited to achieve local privilege escalation.



The perf_group_detach function did not check the event's siblings' attach_state before calling add_event_to_groups(), but remove_on_exec made it possible to call list_del_event() on before detaching from their group, making it possible to use a dangling pointer causing a use-after-free vulnerability.



We recommend upgrading past commit fd0815f632c24878e325821943edccc7fde947a2.

## References
- https://git.kernel.org
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fd0815f632c24878e325821943edccc7fde947a2
- https://kernel.dance/fd0815f632c24878e325821943edccc7fde947a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2235.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2235
- https://security.netapp.com/advisory/ntap-20230609-0002/
