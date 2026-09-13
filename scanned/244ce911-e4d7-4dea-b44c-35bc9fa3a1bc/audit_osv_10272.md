# [H] CVE-2017-14650

## Summary
Severity: High
Advisory: CVE-2017-14650
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14650
Type: osv

## Details
A Remote Code Execution vulnerability has been found in the Horde_Image library when using the "Im" backend that utilizes ImageMagick's "convert" utility. It's not exploitable through any Horde application, because the code path to the vulnerability is not used by any Horde code. Custom applications using the Horde_Image library might be affected. This vulnerability affects all versions of Horde_Image from 2.0.0 to 2.5.1, and is fixed in 2.5.2. The problem is missing input validation of the index field in _raw() during construction of an ImageMagick command line.

## References
- http://www.openwall.com/lists/oss-security/2017/09/21/4
- https://marc.info/?l=horde-announce&m=150600299528079&w=2
- https://www.debian.org/security/2018/dsa-4276
- https://github.com/horde/horde/commit/eb3afd14c22c77ae0d29e2848f5ac726ef6e7c5b
