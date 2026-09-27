# [H] CVE-2021-23521

## Summary
Severity: High
Advisory: CVE-2021-23521
Aliases: SNYK-UNMANAGED-JUCEFRAMEWORKJUCE-2388608
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-31
Source: https://osv.dev/vulnerability/CVE-2021-23521
Type: osv

## Details
This affects the package juce-framework/JUCE before 6.1.5. This vulnerability is triggered when a malicious archive is crafted with an entry containing a symbolic link. When extracted, the symbolic link is followed outside of the target dir allowing writing arbitrary files on the target host. In some cases, this can allow an attacker to execute arbitrary code. The vulnerable code is in the ZipFile::uncompressEntry function in juce_ZipFile.cpp and is executed when the archive is extracted upon calling uncompressTo() on a ZipFile object.

## References
- https://github.com/juce-framework/JUCE/commit/2e874e80cba0152201aff6a4d0dc407997d10a7f
- https://snyk.io/vuln/SNYK-UNMANAGED-JUCEFRAMEWORKJUCE-2388608
