# [M] There's a possible overflow in handle_image() when shim tries to load and execute crafted EFI executables

## Summary
Severity: Medium
Advisory: CVE-2022-28737
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2022-28737
Type: osv

## Details
There's a possible overflow in handle_image() when shim tries to load and execute crafted EFI executables; The handle_image() function takes into account the SizeOfRawData field from each section to be loaded. An attacker can leverage this to perform out-of-bound writes into memory. Arbitrary code execution is not discarded in such scenario.

## References
- https://github.com/rhboot/shim/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/28xxx/CVE-2022-28737.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-28737
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-28737
- https://www.openwall.com/lists/oss-security/2022/06/07/5
