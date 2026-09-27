# [H] CVE-2021-44512

## Summary
Severity: High
Advisory: CVE-2021-44512
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-07
Source: https://osv.dev/vulnerability/CVE-2021-44512
Type: osv

## Details
World-writable permissions on the /tmp/tmate/sessions directory in tmate-ssh-server 2.3.0 allow a local attacker to compromise the integrity of session handling, or obtain the read-write session ID from a read-only session symlink in this directory.

## References
- https://www.openwall.com/lists/oss-security/2021/12/06/2
- https://github.com/tmate-io/tmate-ssh-server/commit/1c020d1f5ca462f5b150b46a027aaa1bbe3c9596
