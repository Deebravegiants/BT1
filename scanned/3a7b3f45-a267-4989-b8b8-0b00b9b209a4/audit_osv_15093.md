# [H] CVE-2019-13338

## Summary
Severity: High
Advisory: CVE-2019-13338
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-09
Source: https://osv.dev/vulnerability/CVE-2019-13338
Type: osv

## Details
In WESEEK GROWI before 3.5.0, a remote attacker can obtain the password hash of the creator of a page by leveraging wiki access to make API calls for page metadata. In other words, the password hash can be retrieved even though it is not a publicly available field.

## References
- https://gist.github.com/polkaman/d039fb5236a043907e44efc198d9161c
