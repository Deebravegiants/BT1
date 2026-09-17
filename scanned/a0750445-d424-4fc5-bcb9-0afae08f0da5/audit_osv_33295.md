# [M] RefindPlusRepo RefindPlus RP_ApfsIo.c InternalApfsTranslateBlock null pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2025-4003
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-28
Source: https://osv.dev/vulnerability/CVE-2025-4003
Type: osv

## Details
A vulnerability was found in RefindPlusRepo RefindPlus 0.14.2.AB. It has been classified as problematic. This affects the function InternalApfsTranslateBlock of the file Library/RP_ApfsLib/RP_ApfsIo.c. The manipulation leads to null pointer dereference. It is possible to launch the attack on the local host. The patch is named 4d35125ca689a255647e9033dd60c257d26df7cb. It is recommended to apply a patch to fix this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4003.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4003
- https://vuldb.com/?id.306339
- https://vuldb.com/?submit.558123
- https://github.com/RefindPlusRepo/RefindPlus/issues/206
- https://github.com/RefindPlusRepo/RefindPlus/issues/206#event-16595888967
- https://vuldb.com/?ctiid.306339
- https://github.com/RefindPlusRepo/RefindPlus/commit/4d35125ca689a255647e9033dd60c257d26df7cb
