# [M] CVE-2017-6198

## Summary
Severity: Medium
Advisory: CVE-2017-6198
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2017-6198
Type: osv

## Details
The Supervisor in Sandstorm doesn't set and enforce the resource limits of a process. This allows remote attackers to cause a denial of service by launching a fork bomb in the sandbox, or by using a large amount of disk space.

## References
- https://github.com/sandstorm-io/sandstorm/blob/v0.202/src/sandstorm/supervisor.c++#L824
- https://devco.re/blog/2018/01/26/Sandstorm-Security-Review-CVE-2017-6200-en/
