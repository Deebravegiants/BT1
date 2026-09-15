# [M] RansomLook Missing Authorization Allows Disclosure of Private Group and Ransom Note Data

## Summary
Severity: Medium
Advisory: CVE-2026-78372
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78372
Type: osv

## Details
RansomLook does not consistently 
enforce authorization checks when accessing groups, markets, and ransom 
notes marked as private. An unauthenticated or otherwise unauthorized 
remote attacker can access information associated with private entities 
through several web views and API endpoints.


The affected functionality can 
disclose private group or market names, ransom-note content, and 
metadata associated with private groups. The /compare
 functionality can also be queried directly with the name of a private 
entity, allowing an unauthorized user to retrieve information such as 
post counts, mirror totals, and uptime even when the entity is excluded 
from the normal user interface. The patch explicitly adds a privacy 
check before returning this information. 


Ransom-note views, search results, 
and API endpoints were similarly missing consistent filtering. The fix 
introduces normalized private-group identifiers and alias handling, then
 rejects or filters notes associated with private groups before 
returning them to unauthorized callers.  


An attacker can exploit the issue 
remotely without authentication or user interaction, resulting in 
disclosure of information that was explicitly intended to be restricted 
to authorized users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78372.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78372
- https://github.com/RansomLook/RansomLook/commit/dc92d6d5c076bcdbf3476aca42daf0260e8d99d7
- https://github.com/RansomLook/RansomLook
