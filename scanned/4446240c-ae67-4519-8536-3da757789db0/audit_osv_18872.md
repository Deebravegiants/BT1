# [C] CVE-2020-36639

## Summary
Severity: Critical
Advisory: CVE-2020-36639
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-04
Source: https://osv.dev/vulnerability/CVE-2020-36639
Type: osv

## Details
A vulnerability has been found in AlliedModders AMX Mod X on Windows and classified as critical. This vulnerability affects the function cmdVoteMap of the file plugins/adminvote.sma of the component Console Command Handler. The manipulation of the argument amx_votemap leads to path traversal. The patch is identified as a5f2b5539f6d61050b68df8b22ebb343a2862681. It is recommended to apply a patch to fix this issue. VDB-217354 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?ctiid.217354
- https://vuldb.com/?id.217354
- https://github.com/alliedmodders/amxmodx/commit/a5f2b5539f6d61050b68df8b22ebb343a2862681
- https://github.com/alliedmodders/amxmodx/pull/823
