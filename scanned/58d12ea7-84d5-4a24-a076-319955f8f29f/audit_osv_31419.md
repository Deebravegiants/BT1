# [M] OpenSupports 4.11.0 — Insecure Direct Object Reference in supervised list

## Summary
Severity: Medium
Advisory: CVE-2025-10696
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-10696
Type: osv

## Details
OpenSupports exposes an endpoint that allows the list of 'supervised users' for any account to be edited, but it does not validate whether the actor is the owner of that list. A Level 1 staff member can modify the supervision relationship of a third party (the target user), who can then view the tickets of the added 'supervised' users. This breaks the authorization model and filters the content of other users' tickets.This issue affects OpenSupports: 4.11.0.

## References
- https://fluidattacks.com/advisories/stratovarius
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10696.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10696
- https://github.com/opensupports/opensupports
