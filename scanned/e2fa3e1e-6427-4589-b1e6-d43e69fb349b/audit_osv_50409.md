# [M] CVE-2020-15566

## Summary
Severity: Medium
Advisory: CVE-2020-15566
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/CVE-2020-15566
Type: osv

## Details
An issue was discovered in Xen through 4.13.x, allowing guest OS users to cause a host OS crash because of incorrect error handling in event-channel port allocation. The allocation of an event-channel port may fail for multiple reasons: (1) port is already in use, (2) the memory allocation failed, or (3) the port we try to allocate is higher than what is supported by the ABI (e.g., 2L or FIFO) used by the guest or the limit set by an administrator (max_event_channels in xl cfg). Due to the missing error checks, only (1) will be considered an error. All the other cases will provide a valid port and will result in a crash when trying to access the event channel. When the administrator configured a guest to allow more than 1023 event channels, that guest may be able to crash the host. When Xen is out-of-memory, allocation of new event channels will result in crashing the host rather than reporting an error. Xen versions 4.10 and later are affected. All architectures are affected. The default configuration, when guests are created with xl/libxl, is not vulnerable, because of the default event-channel limit.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00031.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MXESCOVI7AVRNC7HEAMFM7PMEO6D3AUH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VB3QJJZV23Z2IDYEMIHELWYSQBUEW6JP/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00024.html
- http://www.openwall.com/lists/oss-security/2020/07/07/2
- http://xenbits.xen.org/xsa/advisory-317.html
- https://security.gentoo.org/glsa/202007-02
- https://www.debian.org/security/2020/dsa-4723
