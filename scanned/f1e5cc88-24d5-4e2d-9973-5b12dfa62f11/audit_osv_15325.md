# [M] CVE-2019-15523

## Summary
Severity: Medium
Advisory: CVE-2019-15523
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-12-30
Source: https://osv.dev/vulnerability/CVE-2019-15523
Type: osv

## Details
An issue was discovered in LINBIT csync2 through 2.0. It does not correctly check for the return value GNUTLS_E_WARNING_ALERT_RECEIVED of the gnutls_handshake() function. It neglects to call this function again, as required by the design of the API.

## References
- https://lists.debian.org/debian-lts-announce/2021/01/msg00003.html
- https://github.com/LINBIT/csync2/pull/13/commits/92742544a56bcbcd9ec99ca15f898b31797e39e2
