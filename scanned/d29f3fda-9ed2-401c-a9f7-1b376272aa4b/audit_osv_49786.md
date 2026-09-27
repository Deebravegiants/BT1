# [M] CVE-2019-19065

## Summary
Severity: Medium
Advisory: CVE-2019-19065
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19065
Type: osv

## Details
A memory leak in the sdma_init() function in drivers/infiniband/hw/hfi1/sdma.c in the Linux kernel before 5.3.9 allows attackers to cause a denial of service (memory consumption) by triggering rhashtable_init() failures, aka CID-34b3be18a04e. NOTE: This has been disputed as not a vulnerability because "rhashtable_init() can only fail if it is passed invalid values in the second parameter's struct, but when invoked from sdma_init() that is a pointer to a static const struct, so an attacker could only trigger failure if they could corrupt kernel memory (in which case a small memory leak is not a significant problem).

## References
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4210-1/
- https://usn.ubuntu.com/4226-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://github.com/torvalds/linux/commit/34b3be18a04ecdc610aae4c48e5d1b799d8689f6
