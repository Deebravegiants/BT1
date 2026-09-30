# [H] CVE-2017-0910

## Summary
Severity: High
Advisory: CVE-2017-0910
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-0910
Type: osv

## Details
In Zulip Server before 1.7.1, on a server with multiple realms, a vulnerability in the invitation system lets an authorized user of one realm on the server create a user account on any other realm.

## References
- http://blog.zulip.org/2017/11/23/zulip-1-7-1-released/
- https://github.com/zulip/zulip/commit/960d736e55cbb9386a68e4ee45f80581fd2a4e32
