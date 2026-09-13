# [M] CVE-2021-27851

## Summary
Severity: Medium
Advisory: CVE-2021-27851
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/CVE-2021-27851
Type: osv

## Details
A security vulnerability that can lead to local privilege escalation has been found in ’guix-daemon’. It affects multi-user setups in which ’guix-daemon’ runs locally. The attack consists in having an unprivileged user spawn a build process, for instance with `guix build`, that makes its build directory world-writable. The user then creates a hardlink to a root-owned file such as /etc/shadow in that build directory. If the user passed the --keep-failed option and the build eventually fails, the daemon changes ownership of the whole build tree, including the hardlink, to the user. At that point, the user has write access to the target file. Versions after and including v0.11.0-3298-g2608e40988, and versions prior to v1.2.0-75109-g94f0312546 are vulnerable.

## References
- https://bugs.gnu.org/47229
- https://guix.gnu.org/en/blog/2021/risk-of-local-privilege-escalation-via-guix-daemon/
