# [M] CVE-2021-20290

## Summary
Severity: Medium
Advisory: CVE-2021-20290
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-20290
Type: osv

## Details
An improper authorization handling flaw was found in Foreman. The OpenSCAP plugin for the smart-proxy allows foreman clients to execute actions that should be limited to the Foreman Server. This flaw allows an authenticated local attacker to access and delete limited resources and also causes a denial of service on the Foreman server. The highest threat from this vulnerability is to integrity and system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1939701
