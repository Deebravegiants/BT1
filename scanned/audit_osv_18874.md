# [H] CVE-2020-36646

## Summary
Severity: High
Advisory: CVE-2020-36646
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-07
Source: https://osv.dev/vulnerability/CVE-2020-36646
Type: osv

## Details
A vulnerability classified as problematic has been found in MediaArea ZenLib up to 0.4.38. This affects the function Ztring::Date_From_Seconds_1970_Local of the file Source/ZenLib/Ztring.cpp. The manipulation of the argument Value leads to unchecked return value to null pointer dereference. Upgrading to version 0.4.39 is able to address this issue. The identifier of the patch is 6475fcccd37c9cf17e0cfe263b5fe0e2e47a8408. It is recommended to upgrade the affected component. The identifier VDB-217629 was assigned to this vulnerability.

## References
- https://github.com/MediaArea/ZenLib/releases/tag/v0.4.39
- https://vuldb.com/?ctiid.217629
- https://vuldb.com/?id.217629
- https://github.com/MediaArea/ZenLib/commit/6475fcccd37c9cf17e0cfe263b5fe0e2e47a8408
- https://github.com/MediaArea/ZenLib/pull/119
