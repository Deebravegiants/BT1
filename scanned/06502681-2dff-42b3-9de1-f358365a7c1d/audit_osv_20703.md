# [H] CVE-2021-3626

## Summary
Severity: High
Advisory: CVE-2021-3626
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-10-01
Source: https://osv.dev/vulnerability/CVE-2021-3626
Type: osv

## Details
The Windows version of Multipass before 1.7.0 allowed any local process to connect to the localhost TCP control socket to perform mounts from the operating system to a guest, allowing for privilege escalation.

## References
- https://github.com/canonical/multipass/pull/2150
