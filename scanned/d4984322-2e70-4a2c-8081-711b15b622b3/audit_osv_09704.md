# [C] CVE-2017-10966

## Summary
Severity: Critical
Advisory: CVE-2017-10966
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/CVE-2017-10966
Type: osv

## Details
An issue was discovered in Irssi before 1.0.4. While updating the internal nick list, Irssi could incorrectly use the GHashTable interface and free the nick while updating it. This would then result in use-after-free conditions on each access of the hash table.

## References
- https://www.debian.org/security/2017/dsa-4016
- https://github.com/irssi/irssi/commit/5e26325317c72a04c1610ad952974e206384d291
- https://irssi.org/security/irssi_sa_2017_07.txt
