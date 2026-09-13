# [H] CVE-2019-15136

## Summary
Severity: High
Advisory: CVE-2019-15136
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15136
Type: osv

## Details
The Access Control plugin in eProsima Fast RTPS through 1.9.0 does not check partition permissions from remote participant connections, which can lead to policy bypass for a secure Data Distribution Service (DDS) partition.

## References
- https://arxiv.org/abs/1908.05310
- https://github.com/eProsima/Fast-RTPS/issues/443
