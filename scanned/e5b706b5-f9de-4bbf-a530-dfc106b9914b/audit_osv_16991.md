# [M] CVE-2020-11047

## Summary
Severity: Medium
Advisory: CVE-2020-11047
Aliases: GHSA-9fw6-m2q8-h5pw
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-05-07
Source: https://osv.dev/vulnerability/CVE-2020-11047
Type: osv

## Details
In FreeRDP after 1.1 and before 2.0.0, there is an out-of-bounds read in autodetect_recv_bandwidth_measure_results. A malicious server can extract up to 8 bytes of client memory with a manipulated message by providing a short input and reading the measurement result data. This has been patched in 2.0.0.

## References
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-9fw6-m2q8-h5pw
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://usn.ubuntu.com/4379-1/
- https://github.com/FreeRDP/FreeRDP/commit/f5e73cc7c9cd973b516a618da877c87b80950b65
- https://github.com/FreeRDP/FreeRDP/issues/6009
