# [M] pstore/zone: Add a null pointer check to the psz_kmsg_read

## Summary
Severity: Medium
Advisory: CVE-2024-35940
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35940
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.215, >=5.11.0 <5.15.155, >=5.16.0 <6.1.86, >=6.2.0 <6.6.27, >=6.7.0 <6.8.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

pstore/zone: Add a null pointer check to the psz_kmsg_read

kasprintf() returns a pointer to dynamically allocated memory
which can be NULL upon failure. Ensure the allocation was successful
by checking the pointer validity.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0ff96ec22a84d80a18d7ae8ca7eb111c34ee33bb
- https://git.kernel.org/stable/c/635594cca59f9d7a8e96187600c34facb8bc0682
- https://git.kernel.org/stable/c/6f9f2e498eae7897ba5d3e33908917f68ff4abcc
- https://git.kernel.org/stable/c/98bc7e26e14fbb26a6abf97603d59532475e97f8
- https://git.kernel.org/stable/c/98e2b97acb875d65bdfc75fc408e67975cef3041
- https://git.kernel.org/stable/c/ec7256887d072f98c42cdbef4dcc80ddf84c7a70
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35940.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35940
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
