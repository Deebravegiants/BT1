# [M] CVE-2018-5806

## Summary
Severity: Medium
Advisory: CVE-2018-5806
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-5806
Type: osv

## Details
An error within the "leaf_hdr_load_raw()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.8 can be exploited to trigger a NULL pointer dereference.

## References
- https://access.redhat.com/errata/RHSA-2018:3065
- https://github.com/LibRaw/LibRaw/blob/master/Changelog.txt
- https://secuniaresearch.flexerasoftware.com/advisories/81000/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2018-3/
- https://github.com/LibRaw/LibRaw/commit/9f26ce37f5be86ea11bfc6831366558650b1f6ff
