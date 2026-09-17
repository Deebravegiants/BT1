# [H] CVE-2021-33505

## Summary
Severity: High
Advisory: CVE-2021-33505
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-15
Source: https://osv.dev/vulnerability/CVE-2021-33505
Type: osv

## Details
A local malicious user can circumvent the Falco detection engine through 0.28.1 by running a program that alters arguments of system calls being executed. Issue is fixed in Falco versions >= 0.29.1.

## References
- https://github.com/falcosecurity/falco/releases
- https://github.com/falcosecurity/falco/pull/1675
