# [H] CVE-2017-18641

## Summary
Severity: High
Advisory: CVE-2017-18641
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-10
Source: https://osv.dev/vulnerability/CVE-2017-18641
Type: osv

## Details
In LXC 2.0, many template scripts download code over cleartext HTTP, and omit a digital-signature check, before running it to bootstrap containers.

## References
- https://bugs.launchpad.net/ubuntu/+source/lxc/+bug/1661447
