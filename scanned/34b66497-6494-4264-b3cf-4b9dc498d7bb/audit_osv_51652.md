# [C] CVE-2021-3781

## Summary
Severity: Critical
Advisory: CVE-2021-3781
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-3781
Type: osv

## Details
A trivial sandbox (enabled with the `-dSAFER` option) escape flaw was found in the ghostscript interpreter by injecting a specially crafted pipe command. This flaw allows a specially crafted document to execute arbitrary commands on the system in the context of the ghostscript interpreter. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.gentoo.org/glsa/202211-11
- https://bugzilla.redhat.com/show_bug.cgi?id=2002271
- https://ghostscript.com/CVE-2021-3781.html
