# [M] CVE-2020-25601

## Summary
Severity: Medium
Advisory: CVE-2020-25601
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/CVE-2020-25601
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. There is a lack of preemption in evtchn_reset() / evtchn_destroy(). In particular, the FIFO event channel model allows guests to have a large number of event channels active at a time. Closing all of these (when resetting all event channels or when cleaning up after the guest) may take extended periods of time. So far, there was no arrangement for preemption at suitable intervals, allowing a CPU to spend an almost unbounded amount of time in the processing of these operations. Malicious or buggy guest kernels can mount a Denial of Service (DoS) attack affecting the entire system. All Xen versions are vulnerable in principle. Whether versions 4.3 and older are vulnerable depends on underlying hardware characteristics.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4JRXMKEMQRQYWYEPHVBIWUEAVQ3LU4FN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DA633Y3G5KX7MKRN4PFEGM3IVTJMBEOM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RJZERRBJN6E6STDCHT4JHP4MI6TKBCJE/
- https://www.debian.org/security/2020/dsa-4769
- https://xenbits.xen.org/xsa/advisory-344.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00008.html
- https://security.gentoo.org/glsa/202011-06
