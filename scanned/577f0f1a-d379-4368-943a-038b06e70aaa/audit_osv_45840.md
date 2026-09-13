# [C] JLSEC-2026-394

## Summary
Severity: Critical
Advisory: JLSEC-2026-394
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-394
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=7.70.0+0 <7.84.0+0

## Details
When curl < 7.84.0 saves cookies, alt-svc and hsts data to local files, it makes the operation atomic by finalizing the operation with a rename from a temporary name to the final target file name.In that rename operation, it might accidentally *widen* the permissions for the target file, leaving the updated file accessible to more users than intended.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
- https://hackerone.com/reports/1573634
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEV6BR4MTI3CEWK2YU2HQZUW5FAS3FEY/
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220915-0003/
- https://support.apple.com/kb/HT213488
- https://www.debian.org/security/2022/dsa-5197
