# [M] CVE-2020-10689

## Summary
Severity: Medium
Advisory: CVE-2020-10689
CVSS: 6.8 (CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-03
Source: https://osv.dev/vulnerability/CVE-2020-10689
Type: osv

## Details
A flaw was found in the Eclipse Che up to version 7.8.x, where it did not properly restrict access to workspace pods. An authenticated user can exploit this flaw to bypass JWT proxy and gain access to the workspace pods of another user. Successful exploitation requires knowledge of the service name and namespace of the target pod.

## References
- https://github.com/eclipse/che/issues/15651
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10689
