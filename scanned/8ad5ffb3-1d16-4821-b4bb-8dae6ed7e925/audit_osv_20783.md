# [M] CVE-2021-3695

## Summary
Severity: Medium
Advisory: CVE-2021-3695
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/CVE-2021-3695
Type: osv

## Details
A crafted 16-bit grayscale PNG image may lead to a out-of-bounds write in the heap area. An attacker may take advantage of that to cause heap data corruption or eventually arbitrary code execution and circumvent secure boot protections. This issue has a high complexity to be exploited as an attacker needs to perform some triage over the heap layout to achieve signifcant results, also the values written into the memory are repeated three times in a row making difficult to produce valid payloads. This flaw affects grub2 versions prior grub-2.12.

## References
- https://security.netapp.com/advisory/ntap-20220930-0001/
- https://security.gentoo.org/glsa/202209-12
- https://bugzilla.redhat.com/show_bug.cgi?id=1991685
