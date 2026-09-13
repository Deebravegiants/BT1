# [M] HTTP multi-header compression denial of service

## Summary
Severity: Medium
Advisory: CURL-CVE-2023-23916
Aliases: CVE-2023-23916
Published: 2023-02-15
Source: https://osv.dev/vulnerability/CURL-CVE-2023-23916
Type: osv

## Details
curl supports "chained" HTTP compression algorithms, meaning that a server
response can be compressed multiple times and potentially with different
algorithms. The number of acceptable "links" in this "decompression chain" was
capped, but the cap was implemented on a per-header basis allowing a malicious
server to insert a virtually unlimited number of compression steps by using
many headers.

The use of such a decompression chain could result in a "malloc bomb", making
curl end up spending enormous amounts of allocated heap memory, or trying to
and returning out of memory errors.
