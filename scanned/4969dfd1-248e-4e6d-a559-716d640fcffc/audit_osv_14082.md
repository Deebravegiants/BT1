# [C] CVE-2018-7039

## Summary
Severity: Critical
Advisory: CVE-2018-7039
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-14
Source: https://osv.dev/vulnerability/CVE-2018-7039
Type: osv

## Details
CCN-lite 2.0.0 Beta allows remote attackers to cause a denial of service (buffer overflow) or possibly have unspecified other impact because the ccnl_ndntlv_prependBlob function in ccnl-pkt-ndntlv.c can be called with wrong arguments. Specifically, there is an incorrect integer data type causing a negative third argument in some cases of crafted TLV data with inconsistent length information.

## References
- https://github.com/cn-uofbasel/ccn-lite/issues/191
