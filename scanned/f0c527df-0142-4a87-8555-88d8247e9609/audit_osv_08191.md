# [C] CVE-2016-15007

## Summary
Severity: Critical
Advisory: CVE-2016-15007
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-02
Source: https://osv.dev/vulnerability/CVE-2016-15007
Type: osv

## Details
A vulnerability was found in Centralized-Salesforce-Dev-Framework. It has been declared as problematic. Affected by this vulnerability is the function SObjectService of the file src/classes/SObjectService.cls of the component SOQL Handler. The manipulation of the argument orderDirection leads to injection. The patch is named db03ac5b8a9d830095991b529c067a030a0ccf7b. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-217195.

## References
- https://vuldb.com/?ctiid.217195
- https://vuldb.com/?id.217195
- https://github.com/scottbcovert/Centralized-Salesforce-Dev-Framework/commit/db03ac5b8a9d830095991b529c067a030a0ccf7b
