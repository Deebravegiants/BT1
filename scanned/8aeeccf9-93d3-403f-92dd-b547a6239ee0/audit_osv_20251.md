# [M] CVE-2021-32617

## Summary
Severity: Medium
Advisory: CVE-2021-32617
Aliases: GHSA-w8mv-g8qq-36mj
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-17
Source: https://osv.dev/vulnerability/CVE-2021-32617
Type: osv

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. An inefficient algorithm (quadratic complexity) was found in Exiv2 versions v0.27.3 and earlier. The inefficient algorithm is triggered when Exiv2 is used to write metadata into a crafted image file. An attacker could potentially exploit the vulnerability to cause a denial of service, if they can trick the victim into running Exiv2 on a crafted image file. The bug is fixed in version v0.27.4. Note that this bug is only triggered when _writing_ the metadata, which is a less frequently used Exiv2 operation than _reading_ the metadata. For example, to trigger the bug in the Exiv2 command-line application, you need to add an extra command-line argument such as `rm`.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5I3RRZUGSBIUYZ5TIHLN55PKMAWCSJ5G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M2BPQNJKTRIDINTVJ22QMMTIZEPHVKXK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RQAKFIQHW2AS3AGSJM42ABOA6CWIJBGM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TZ5SGWHK64TB7ADRSVBGHEPDFN5CSOO3/
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/pull/1657
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-w8mv-g8qq-36mj
