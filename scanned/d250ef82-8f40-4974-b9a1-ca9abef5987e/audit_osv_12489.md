# [H] CVE-2018-12520

## Summary
Severity: High
Advisory: CVE-2018-12520
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-12520
Type: osv

## Details
An issue was discovered in ntopng 3.4 before 3.4.180617. The PRNG involved in the generation of session IDs is not seeded at program startup. This results in deterministic session IDs being allocated for active user sessions. An attacker with foreknowledge of the operating system and standard library in use by the host running the service and the username of the user whose session they're targeting can abuse the deterministic random number generation in order to hijack the user's session, thus escalating their access.

## References
- https://github.com/ntop/ntopng/commit/30610bda60cbfc058f90a1c0a17d0e8f4516221a
- http://seclists.org/fulldisclosure/2018/Jul/14
- https://gist.github.com/Psychotropos/3e8c047cada9b1fb716e6a014a428b7f
- https://www.exploit-db.com/exploits/44973/
