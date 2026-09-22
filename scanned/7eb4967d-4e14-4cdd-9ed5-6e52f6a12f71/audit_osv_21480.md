# [C] CVE-2021-4336

## Summary
Severity: Critical
Advisory: CVE-2021-4336
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-28
Source: https://osv.dev/vulnerability/CVE-2021-4336
Type: osv

## Details
A vulnerability was found in ITRS Group monitor-ninja up to 2021.11.1. It has been rated as critical. Affected by this issue is some unknown functionality of the file modules/reports/models/scheduled_reports.php. The manipulation leads to sql injection. Upgrading to version 2021.11.30 is able to address this issue. The name of the patch is 6da9080faec9bca1ca5342386c0421dca0a6c0cc. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-230084.

## References
- https://github.com/ITRS-Group/monitor-ninja/releases/tag/v2021.11.30
- https://vuldb.com/?id.230084
- https://vuldb.com/?ctiid.230084
- https://github.com/ITRS-Group/monitor-ninja/commit/6da9080faec9bca1ca5342386c0421dca0a6c0cc
