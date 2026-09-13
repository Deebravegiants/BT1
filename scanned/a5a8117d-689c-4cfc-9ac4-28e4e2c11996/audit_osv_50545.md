# [M] CVE-2020-1776

## Summary
Severity: Medium
Advisory: CVE-2020-1776
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-07-20
Source: https://osv.dev/vulnerability/CVE-2020-1776
Type: osv

## Details
When an agent user is renamed or set to invalid the session belonging to the user is keept active. The session can not be used to access ticket data in the case the agent is invalid. This issue affects ((OTRS)) Community Edition: 6.0.28 and prior versions. OTRS: 7.0.18 and prior versions, 8.0.4. and prior versions.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00040.html
- https://otrs.com/release-notes/otrs-security-advisory-2020-13/
