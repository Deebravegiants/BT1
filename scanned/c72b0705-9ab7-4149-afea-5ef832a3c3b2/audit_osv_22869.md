# [M] MZ Automation libiec61850 MMS File Services mms_client_files.c path traversal

## Summary
Severity: Medium
Advisory: CVE-2022-3976
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/CVE-2022-3976
Type: osv

## Details
A vulnerability has been found in MZ Automation libiec61850 up to 1.4 and classified as critical. This vulnerability affects unknown code of the file src/mms/iso_mms/client/mms_client_files.c of the component MMS File Services. The manipulation of the argument filename leads to path traversal. Upgrading to version 1.5 is able to address this issue. The name of the patch is 10622ba36bb3910c151348f1569f039ecdd8786f. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-213556.

## References
- https://vuldb.com/?id.213556
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3976.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3976
- https://github.com/mz-automation/libiec61850/commit/10622ba36bb3910c151348f1569f039ecdd8786f
- https://github.com/mz-automation/libiec61850
