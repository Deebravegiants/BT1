# [M] CVE-2020-36827

## Summary
Severity: Medium
Advisory: CVE-2020-36827
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-03-24
Source: https://osv.dev/vulnerability/CVE-2020-36827
Type: osv

## Details
The XAO::Web module before 1.84 for Perl mishandles < and > characters in JSON output during use of json-embed in Web::Action.

## References
- https://metacpan.org/dist/XAO-Web/changes
- https://github.com/amaltsev/XAO-Web/commit/20dd1d3bc5b811503f5722a16037b60197fe7ef4
