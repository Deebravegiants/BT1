# [M] usb: dwc3: gadget: Fix looping of queued SG entries

## Summary
Severity: Medium
Advisory: CVE-2024-56698
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56698
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3: gadget: Fix looping of queued SG entries

The dwc3_request->num_queued_sgs is decremented on completion. If a
partially completed request is handled, then the
dwc3_request->num_queued_sgs no longer reflects the total number of
num_queued_sgs (it would be cleared).

Correctly check the number of request SG entries remained to be prepare
and queued. Failure to do this may cause null pointer dereference when
accessing non-existent SG entry.

## References
- https://git.kernel.org/stable/c/0247da93bf62d33304b7bf97850ebf2a86e06d28
- https://git.kernel.org/stable/c/1534f6f69393aac773465d80d31801b554352627
- https://git.kernel.org/stable/c/70777a23a54e359cfdfafc625a57cd56434f3859
- https://git.kernel.org/stable/c/8ceb21d76426bbe7072cc3e43281e70c0d664cc7
- https://git.kernel.org/stable/c/b7c3d0b59213ebeedff63d128728ce0b3d7a51ec
- https://git.kernel.org/stable/c/b7fc65f5141c24785dc8c19249ca4efcf71b3524
- https://git.kernel.org/stable/c/c9e72352a10ae89a430449f7bfeb043e75c255d9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56698.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56698
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
