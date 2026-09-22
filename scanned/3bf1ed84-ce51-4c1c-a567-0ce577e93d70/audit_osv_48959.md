# [H] CVE-2018-18559

## Summary
Severity: High
Advisory: CVE-2018-18559
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-22
Source: https://osv.dev/vulnerability/CVE-2018-18559
Type: osv

## Details
In the Linux kernel through 4.19, a use-after-free can occur due to a race condition between fanout_add from setsockopt and bind on an AF_PACKET socket. This issue exists because of the 15fe076edea787807a7cdc168df832544b58eba6 incomplete fix for a race condition. The code mishandles a certain multithreaded case involving a packet_do_bind unregister action followed by a packet_notifier register action. Later, packet_release operates on only one of the two applicable linked lists. The attacker can achieve Program Counter control.

## References
- https://access.redhat.com/errata/RHSA-2019:1170
- https://access.redhat.com/errata/RHSA-2019:3967
- https://access.redhat.com/errata/RHSA-2019:4159
- https://access.redhat.com/errata/RHSA-2019:0188
- https://access.redhat.com/errata/RHSA-2019:1190
- https://access.redhat.com/errata/RHSA-2020:0174
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:0163
- https://blogs.securiteam.com/index.php/archives/3731
