# [C] CVE-2018-6953

## Summary
Severity: Critical
Advisory: CVE-2018-6953
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-6953
Type: osv

## Details
In CCN-lite 2, the Parser of NDNTLV does not verify whether a certain component's length field matches the actual component length, which has a resultant buffer overflow and out-of-bounds memory accesses.

## References
- https://github.com/cn-uofbasel/ccn-lite/issues/195
