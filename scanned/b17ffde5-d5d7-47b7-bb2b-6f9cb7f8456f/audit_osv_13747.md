# [C] CVE-2018-25075

## Summary
Severity: Critical
Advisory: CVE-2018-25075
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-15
Source: https://osv.dev/vulnerability/CVE-2018-25075
Type: osv

## Details
A vulnerability classified as critical has been found in karsany OBridge up to 1.3. Affected is the function getAllStandaloneProcedureAndFunction of the file obridge-main/src/main/java/org/obridge/dao/ProcedureDao.java. The manipulation leads to sql injection. The complexity of an attack is rather high. The exploitability is told to be difficult. Upgrading to version 1.4 is able to address this issue. The name of the patch is 52eca4ad05f3c292aed3178b2f58977686ffa376. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-218376.

## References
- https://github.com/karsany/obridge/releases/tag/v1.4
- https://vuldb.com/?id.218376
- https://vuldb.com/?ctiid.218376
- https://github.com/karsany/obridge/commit/52eca4ad05f3c292aed3178b2f58977686ffa376
