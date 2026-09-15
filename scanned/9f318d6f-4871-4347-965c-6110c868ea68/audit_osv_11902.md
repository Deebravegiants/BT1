# [M] CVE-2018-1000040

## Summary
Severity: Medium
Advisory: CVE-2018-1000040
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-24
Source: https://osv.dev/vulnerability/CVE-2018-1000040
Type: osv

## Details
In Artifex MuPDF 1.12.0 and earlier, multiple use of uninitialized value bugs in the PDF parser could allow an attacker to cause a denial of service (crash) or influence program flow via a crafted file.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Ba=commitdiff%3Bh=83d4dae44c71816c084a635550acc1a51529b881%3Bhp=f597300439e62f5e921f0d7b1e880b5c1a1f1607
- https://bugs.ghostscript.com/show_bug.cgi?id=698904
- https://bugs.ghostscript.com/show_bug.cgi?id=699086
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=ace9e69017c08e1e4ce5912014177414c0382004
- https://security.gentoo.org/glsa/201811-15
- https://www.debian.org/security/2018/dsa-4334
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5596
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5600
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5603
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5610
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5609
