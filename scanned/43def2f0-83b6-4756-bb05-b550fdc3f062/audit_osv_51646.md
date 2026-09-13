# [M] CVE-2021-3759

## Summary
Severity: Medium
Advisory: CVE-2021-3759
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3759
Type: osv

## Details
A memory overflow vulnerability was found in the Linux kernel’s ipc functionality of the memcg subsystem, in the way a user calls the semget function multiple times, creating semaphores. This flaw allows a local user to starve the resources, causing a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lore.kernel.org/linux-mm/1626333284-1404-1-git-send-email-nglaive%40gmail.com/
- https://access.redhat.com/security/cve/CVE-2021-3759
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1999675
