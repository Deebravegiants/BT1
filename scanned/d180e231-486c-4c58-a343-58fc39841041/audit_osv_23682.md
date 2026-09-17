# [C] CVE-2022-4933

## Summary
Severity: Critical
Advisory: CVE-2022-4933
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-20
Source: https://osv.dev/vulnerability/CVE-2022-4933
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in ATM Consulting dolibarr_module_quicksupplierprice up to 1.1.6. Affected by this issue is the function upatePrice of the file script/interface.php. The manipulation leads to sql injection. The attack may be launched remotely. Upgrading to version 1.1.7 is able to address this issue. The patch is identified as ccad1e4282b0e393a32fcc852e82ec0e0af5446f. It is recommended to upgrade the affected component. VDB-223382 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?ctiid.223382
- https://vuldb.com/?id.223382
- https://github.com/ATM-Consulting/dolibarr_module_quicksupplierprice/pull/21
- https://github.com/ATM-Consulting/dolibarr_module_quicksupplierprice/commit/ccad1e4282b0e393a32fcc852e82ec0e0af5446f
