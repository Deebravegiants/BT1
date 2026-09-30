# [H] CVE-2018-16882

## Summary
Severity: High
Advisory: CVE-2018-16882
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-01-03
Source: https://osv.dev/vulnerability/CVE-2018-16882
Type: osv

## Details
A use-after-free issue was found in the way the Linux kernel's KVM hypervisor processed posted interrupts when nested(=1) virtualization is enabled. In nested_get_vmcs12_pages(), in case of an error while processing posted interrupt address, it unmaps the 'pi_desc_page' without resetting 'pi_desc' descriptor address, which is later used in pi_test_and_clear_on(). A guest user/process could use this flaw to crash the host kernel resulting in DoS or potentially gain privileged access to a system. Kernel versions before 4.14.91 and before 4.19.13 are vulnerable.

## References
- https://usn.ubuntu.com/3871-4/
- https://usn.ubuntu.com/3871-5/
- https://usn.ubuntu.com/3872-1/
- https://usn.ubuntu.com/3878-1/
- https://lwn.net/Articles/775720/
- https://support.f5.com/csp/article/K80557033
- https://usn.ubuntu.com/3871-1/
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3878-2/
- http://www.securityfocus.com/bid/106254
- https://lwn.net/Articles/775721/
- https://marc.info/?l=kvm&m=154514994222809&w=2
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16882
