# [C] CVE-2019-1010039

## Summary
Severity: Critical
Advisory: CVE-2019-1010039
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010039
Type: osv

## Details
uLaunchELF < commit 170827a is affected by: Buffer Overflow. The impact is: Possible code execution and denial of service. The component is: Loader program (loader.c) overly trusts the arguments provided via command line.

## References
- https://github.com/AKuHAK/uLaunchELF/issues/14
