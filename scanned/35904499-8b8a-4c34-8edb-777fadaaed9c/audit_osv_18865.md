# [C] CVE-2020-36631

## Summary
Severity: Critical
Advisory: CVE-2020-36631
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/CVE-2020-36631
Type: osv

## Details
A vulnerability was found in barronwaffles dwc_network_server_emulator. It has been declared as critical. This vulnerability affects the function update_profile of the file gamespy/gs_database.py. The manipulation of the argument firstname/lastname leads to sql injection. The attack can be initiated remotely. The name of the patch is f70eb21394f75019886fbc2fb536de36161ba422. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-216772.

## References
- https://vuldb.com/?ctiid.216772
- https://vuldb.com/?id.216772
- https://github.com/barronwaffles/dwc_network_server_emulator/commit/f70eb21394f75019886fbc2fb536de36161ba422
- https://github.com/barronwaffles/dwc_network_server_emulator/pull/538
