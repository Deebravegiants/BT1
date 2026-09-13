# [H] CVE-2021-46991

## Summary
Severity: High
Advisory: CVE-2021-46991
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46991
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: Fix use-after-free in i40e_client_subtask()

Currently the call to i40e_client_del_instance frees the object
pf->cinst, however pf->cinst->lan_info is being accessed after
the free. Fix this by adding the missing return.

Addresses-Coverity: ("Read from pointer after free")

## References
- https://git.kernel.org/stable/c/1fd5d262e7442192ac7611ff1597a36c5b044323
- https://git.kernel.org/stable/c/38318f23a7ef86a8b1862e5e8078c4de121960c3
- https://git.kernel.org/stable/c/4ebc10aa7cd17fd9857dedac69600465c9dd16d1
- https://git.kernel.org/stable/c/829a713450b8fb127cbabfc1244c1d8179ec5107
- https://git.kernel.org/stable/c/c1322eaeb8af0d8985b5cc5fa759140fa0e57b84
- https://git.kernel.org/stable/c/d718c15a2bf9ae082d5ae4d177fb19ef23cb4132
