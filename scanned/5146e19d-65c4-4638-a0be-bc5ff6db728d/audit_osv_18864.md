# [C] CVE-2020-36630

## Summary
Severity: Critical
Advisory: CVE-2020-36630
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/CVE-2020-36630
Type: osv

## Details
A vulnerability was found in FreePBX cdr 14.0. It has been classified as critical. This affects the function ajaxHandler of the file ucp/Cdr.class.php. The manipulation of the argument limit/offset leads to sql injection. Upgrading to version 14.0.5.21 is able to address this issue. The name of the patch is f1a9eea2dfff30fb99d825bac194a676a82b9ec8. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216771.

## References
- https://github.com/FreePBX/cdr/releases/tag/release%2F14.0.5.21
- https://vuldb.com/?ctiid.216771
- https://vuldb.com/?id.216771
- https://github.com/FreePBX/cdr/commit/f1a9eea2dfff30fb99d825bac194a676a82b9ec8
