# [M] CVE-2019-11879

## Summary
Severity: Medium
Advisory: CVE-2019-11879
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-10
Source: https://osv.dev/vulnerability/CVE-2019-11879
Type: osv

## Details
The WEBrick gem 1.4.2 for Ruby allows directory traversal if the attacker once had local access to create a symlink to a location outside of the web root directory. NOTE: The vendor states that this is analogous to Options FollowSymlinks in the Apache HTTP Server, and therefore it is "not a problem.

## References
- https://bugs.ruby-lang.org/issues/15835
