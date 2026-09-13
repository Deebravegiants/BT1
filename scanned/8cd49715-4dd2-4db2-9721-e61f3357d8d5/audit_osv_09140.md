# [C] CVE-2016-8597

## Summary
Severity: Critical
Advisory: CVE-2016-8597
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8597
Type: osv

## Details
Buffer overflow in the csp_sfp_recv_fp in csp_sfp.c in the libcsp library v1.4 and earlier allows hostile components with network access to the SFP underlying network layers to execute arbitrary code via specially crafted SFP packets.

## References
- http://www.securityfocus.com/bid/94226
- https://github.com/GomSpace/libcsp/pull/80
