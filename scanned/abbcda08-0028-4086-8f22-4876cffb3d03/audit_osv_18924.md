# [M] CVE-2020-4070

## Summary
Severity: Medium
Advisory: CVE-2020-4070
Aliases: GHSA-wf36-7w73-rh8c
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-4070
Type: osv

## Details
In CSS Validator less than or equal to commit 54d68a1, there is a cross-site scripting vulnerability in handling URIs. A user would have to click on a specifically crafted validator link to trigger it. This has been patched in commit e5c09a9.

## References
- https://github.com/w3c/css-validator/security/advisories/GHSA-wf36-7w73-rh8c
- https://github.com/w3c/css-validator/commit/e5c09a9119167d3064db786d5f00d730b584a53b
