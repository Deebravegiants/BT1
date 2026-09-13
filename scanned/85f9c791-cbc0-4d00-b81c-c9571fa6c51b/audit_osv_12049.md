# [M] CVE-2018-1000852

## Summary
Severity: Medium
Advisory: CVE-2018-1000852
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000852
Type: osv

## Details
FreeRDP FreeRDP 2.0.0-rc3 released version before commit 205c612820dac644d665b5bb1cdf437dc5ca01e3 contains a Other/Unknown vulnerability in channels/drdynvc/client/drdynvc_main.c, drdynvc_process_capability_request that can result in The RDP server can read the client's memory.. This attack appear to be exploitable via RDPClient must connect the rdp server with echo option. This vulnerability appears to have been fixed in after commit 205c612820dac644d665b5bb1cdf437dc5ca01e3.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YVJKO2DR5EY4C4QZOP7SNNBEW2JW6FHX/
- https://access.redhat.com/errata/RHSA-2019:2157
- https://github.com/FreeRDP/FreeRDP/pull/4871
- https://usn.ubuntu.com/4379-1/
- https://github.com/FreeRDP/FreeRDP/pull/4871/commits/baee520e3dd9be6511c45a14c5f5e77784de1471
- https://github.com/FreeRDP/FreeRDP/issues/4866
