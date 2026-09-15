# [M] CVE-2021-30479

## Summary
Severity: Medium
Advisory: CVE-2021-30479
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-04-15
Source: https://osv.dev/vulnerability/CVE-2021-30479
Type: osv

## Details
An issue was discovered in Zulip Server before 3.4. A bug in the implementation of the all_public_streams API feature resulted in guest users being able to receive message traffic to public streams that should have been only accessible to members of the organization.

## References
- https://blog.zulip.com/2021/04/14/zulip-server-3-4/
