# [H] CVE-2021-3456

## Summary
Severity: High
Advisory: CVE-2021-3456
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-03-30
Source: https://osv.dev/vulnerability/CVE-2021-3456
Type: osv

## Details
An improper authorization handling flaw was found in Foreman. The Salt plugin for the smart-proxy allows foreman clients to execute actions that should be limited to the Foreman Server. This flaw allows an authenticated local attacker to access and delete limited resources and also causes a denial of service on the Foreman server. The highest threat from this vulnerability is to integrity and system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1941001
