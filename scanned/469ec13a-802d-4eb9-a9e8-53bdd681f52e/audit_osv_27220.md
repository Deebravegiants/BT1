# [C] Roxy-WI roxy.py action_service os command injection

## Summary
Severity: Critical
Advisory: CVE-2024-13129
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-01-03
Source: https://osv.dev/vulnerability/CVE-2024-13129
Type: osv

## Details
A vulnerability was found in Roxy-WI up to 8.1.3. It has been declared as critical. Affected by this vulnerability is the function action_service of the file app/modules/roxywi/roxy.py. The manipulation of the argument action/service leads to os command injection. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 8.1.4 is able to address this issue. The identifier of the patch is 32313928eb9ce906887b8a30bf7b9a3d5c0de1be. It is recommended to upgrade the affected component.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/13xxx/CVE-2024-13129.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-13129
- https://vuldb.com/?id.290149
- https://vuldb.com/?submit.468530
- https://github.com/roxy-wi/roxy-wi/pull/410
- https://github.com/roxy-wi/roxy-wi/pull/410#issuecomment-2561289700
- https://vuldb.com/?ctiid.290149
- https://github.com/roxy-wi/roxy-wi/pull/410/commits/32313928eb9ce906887b8a30bf7b9a3d5c0de1be
- https://github.com/roxy-wi/roxy-wi/releases/tag/v8.1.4
- https://github.com/0xs1ash/Exploits/tree/main/CVE-EXPLOIT
