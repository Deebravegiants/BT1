# [C] CVE-2021-23520

## Summary
Severity: Critical
Advisory: CVE-2021-23520
Aliases: SNYK-UNMANAGED-JUCEFRAMEWORKJUCE-2388607
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-31
Source: https://osv.dev/vulnerability/CVE-2021-23520
Type: osv

## Details
The package juce-framework/juce before 6.1.5 are vulnerable to Arbitrary File Write via Archive Extraction (Zip Slip) via the ZipFile::uncompressEntry function in juce_ZipFile.cpp. This vulnerability is triggered when the archive is extracted upon calling uncompressTo() on a ZipFile object.

## References
- https://github.com/juce-framework/JUCE/commit/2e874e80cba0152201aff6a4d0dc407997d10a7f
- https://snyk.io/vuln/SNYK-UNMANAGED-JUCEFRAMEWORKJUCE-2388607
- https://snyk.io/research/zip-slip-vulnerability
