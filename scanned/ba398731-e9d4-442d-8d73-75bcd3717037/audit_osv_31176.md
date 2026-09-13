# [H] tls: stop recv() if initial process_rx_list gave us non-DATA

## Summary
Severity: High
Advisory: CVE-2024-58239
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2024-58239
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.270, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: stop recv() if initial process_rx_list gave us non-DATA

If we have a non-DATA record on the rx_list and another record of the
same type still on the queue, we will end up merging them:
 - process_rx_list copies the non-DATA record
 - we start the loop and process the first available record since it's
   of the same type
 - we break out of the loop since the record was not DATA

Just check the record type and jump to the end in case process_rx_list
did some work.

## References
- https://git.kernel.org/stable/c/31e10d6cb0c9532ff070cf50da1657c3acee9276
- https://git.kernel.org/stable/c/3b952d8fdfcf6fd8ea0b8954bc9277642cf0977f
- https://git.kernel.org/stable/c/4338032aa90bd1d5b33a4274e8fa8347cda5ee09
- https://git.kernel.org/stable/c/6756168add1c6c3ef1c32c335bb843a5d1f99a75
- https://git.kernel.org/stable/c/a4ed943882a8fc057ea5a67643314245e048bbdd
- https://git.kernel.org/stable/c/f310143961e2d9a0479fca117ce869f8aaecc140
- https://git.kernel.org/stable/c/fdfbaec5923d9359698cbb286bc0deadbb717504
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58239.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
