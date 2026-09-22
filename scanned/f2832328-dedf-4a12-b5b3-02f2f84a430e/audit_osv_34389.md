# [M] Apache CloudStack: Potential remote code execution on Javascript engine defined rules

## Summary
Severity: Medium
Advisory: CVE-2025-59302
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-11-27
Source: https://osv.dev/vulnerability/CVE-2025-59302
Type: osv

## Details
In  Apache CloudStack improper control of generation of code ('Code Injection') vulnerability is found in the following APIs which are accessible only to admins.

  *  quotaTariffCreate
  *  quotaTariffUpdate
  *  createSecondaryStorageSelector
  *  updateSecondaryStorageSelector
  *  updateHost
  *  updateStorage


This issue affects Apache CloudStack: from 4.18.0 before 4.20.2, from 4.21.0 before 4.22.0. Users are recommended to upgrade to versions 4.20.2 or 4.22.0, which contain the fix.

The fix introduces a new global configuration flag, js.interpretation.enabled, allowing administrators to control the interpretation of JavaScript expressions in these APIs, thereby mitigating the code injection risk.

## References
- http://www.openwall.com/lists/oss-security/2025/11/27/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59302.json
- https://lists.apache.org/thread/kwwsg2j85f1b75o0ht5zbr34d7h66788
- https://nvd.nist.gov/vuln/detail/CVE-2025-59302
