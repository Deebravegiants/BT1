# [M] CVE-2020-14976

## Summary
Severity: Medium
Advisory: CVE-2020-14976
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-23
Source: https://osv.dev/vulnerability/CVE-2020-14976
Type: osv

## Details
GNS3 ubridge through 0.9.18 on macOS, as used in GNS3 server before 2.1.17, allows a local attacker to read arbitrary files because it handles configuration-file errors by printing the configuration file while executing in a setuid root context.

## References
- https://github.com/GNS3/gns3-server/releases/tag/v2.1.17
- https://www.gns3.com/
- https://github.com/GNS3/ubridge/commit/2eb0d1dab6a6de76cf3556130a2d52af101077db
- https://theevilbit.github.io/posts/
