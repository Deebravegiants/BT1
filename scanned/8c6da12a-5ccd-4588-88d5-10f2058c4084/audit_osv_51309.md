# [H] CVE-2021-28375

## Summary
Severity: High
Advisory: CVE-2021-28375
Aliases: A-183188047, ASB-A-183188047
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2021-28375
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.6. fastrpc_internal_invoke in drivers/misc/fastrpc.c does not prevent user applications from sending kernel RPC messages, aka CID-20c40794eb85. This is a related issue to CVE-2019-2308.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OMRQVOTASD3VZP6GE4JJHE27QU6FHTZ6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TJPVQZPY3DHPV5I3IVNMSMO6D3PKZISX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XAUNYDTGE6MB4NWL2SIHPCODCLET3JZB/
- https://lore.kernel.org/stable/YD03ew7+6v0XPh6l%40kroah.com/
- https://security.netapp.com/advisory/ntap-20210401-0003/
- https://git.kernel.org/linus/20c40794eb85ea29852d7bc37c55713802a543d6
