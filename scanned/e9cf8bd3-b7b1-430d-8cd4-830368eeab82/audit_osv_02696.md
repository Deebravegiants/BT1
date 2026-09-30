# [H] ALPINE-CVE-2022-42919

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42919
Ecosystem: Alpine:v3.16, Alpine:v3.17
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42919
Type: osv

## Affected
- Alpine:v3.16: `python3` — affected >=0 <3.10.9-r0
- Alpine:v3.17: `python3` — affected >=0 <3.10.9-r0

## Details
Python 3.9.x before 3.9.16 and 3.10.x before 3.10.9 on Linux allows local privilege escalation in a non-default configuration. The Python multiprocessing library, when used with the forkserver start method on Linux, allows pickles to be deserialized from any user in the same machine local network namespace, which in many system configurations means any user on the same machine. Pickles can execute arbitrary code. Thus, this allows for local user privilege escalation to the user that any forkserver process is running as. Setting multiprocessing.util.abstract_sockets_supported to False is a workaround. The forkserver start method for multiprocessing is not the default start method. This issue is Linux specific because only Linux supports abstract namespace sockets. CPython before 3.9 does not make use of Linux abstract namespace sockets by default. Support for users manually specifying an abstract namespace socket was added as a bugfix in 3.7.8 and 3.8.3, but users would need to make specific uncommon API calls in order to do that in CPython before 3.9.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42919
