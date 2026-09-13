# [C] CVE-2020-14983

## Summary
Severity: Critical
Advisory: CVE-2020-14983
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-22
Source: https://osv.dev/vulnerability/CVE-2020-14983
Type: osv

## Details
The server in Chocolate Doom 3.0.0 and Crispy Doom 5.8.0 doesn't validate the user-controlled num_players value, leading to a buffer overflow. A malicious user can overwrite the server's stack.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00012.html
- https://github.com/chocolate-doom/chocolate-doom/issues/1293
