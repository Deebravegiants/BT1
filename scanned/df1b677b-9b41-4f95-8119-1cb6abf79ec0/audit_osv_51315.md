# [H] CVE-2021-28691

## Summary
Severity: High
Advisory: CVE-2021-28691
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-29
Source: https://osv.dev/vulnerability/CVE-2021-28691
Type: osv

## Details
Guest triggered use-after-free in Linux xen-netback A malicious or buggy network PV frontend can force Linux netback to disable the interface and terminate the receive kernel thread associated with queue 0 in response to the frontend sending a malformed packet. Such kernel thread termination will lead to a use-after-free in Linux netback when the backend is destroyed, as the kernel thread associated with queue 0 will have already exited and thus the call to kthread_stop will be performed against a stale pointer.

## References
- https://security.gentoo.org/glsa/202107-30
- https://security.netapp.com/advisory/ntap-20210805-0002/
- https://xenbits.xenproject.org/xsa/advisory-374.txt
