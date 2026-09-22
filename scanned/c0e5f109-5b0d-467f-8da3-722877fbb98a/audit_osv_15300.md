# [H] CVE-2019-15137

## Summary
Severity: High
Advisory: CVE-2019-15137
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15137
Type: osv

## Details
The Access Control plugin in eProsima Fast RTPS through 1.9.0 allows fnmatch pattern matches with topic name strings (instead of the permission expressions themselves), which can lead to unintended connections between participants in a Data Distribution Service (DDS) network.

## References
- https://arxiv.org/abs/1908.05310
- https://github.com/eProsima/Fast-RTPS/issues/441
