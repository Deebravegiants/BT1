# [H] CVE-2019-9746

## Summary
Severity: High
Advisory: CVE-2019-9746
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2019-9746
Type: osv

## Details
In libwebm before 2019-03-08, a NULL pointer dereference caused by the functions OutputCluster and OutputTracks in webm_info.cc will trigger an abort, which allows a DoS attack, a similar issue to CVE-2018-19212.

## References
- https://bugs.chromium.org/p/webm/issues/detail?id=1605
- https://chromium.googlesource.com/webm/libwebm/+/2427abe0bde234987ed005a3adca461e9a85dfb7
