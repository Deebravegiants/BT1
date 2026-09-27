# [H] CVE-2019-25016

## Summary
Severity: High
Advisory: CVE-2019-25016
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-28
Source: https://osv.dev/vulnerability/CVE-2019-25016
Type: osv

## Details
In OpenDoas from 6.6 to 6.8 the users PATH variable was incorrectly inherited by authenticated executions if the authenticating rule allowed the user to execute any command. Rules that only allowed to authenticated user to execute specific commands were not affected by this issue.

## References
- https://github.com/Duncaen/OpenDoas/releases/tag/v6.8.1
- https://security.gentoo.org/glsa/202107-11
- https://github.com/Duncaen/OpenDoas/issues/45
- https://github.com/Duncaen/OpenDoas/commit/01c658f8c45cb92a343be5f32aa6da70b2032168
- https://github.com/Duncaen/OpenDoas/commit/d5acd52e2a15c36a8e06f9103d35622933aa422d
