# [M] Arbitrary file write is possible in Pandoc when using PDF output or --extract-media with untrusted input

## Summary
Severity: Medium
Advisory: CVE-2023-35936
Aliases: GHSA-xj5q-fv23-575g, HSEC-2023-0014
CVSS: 6.1 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:N/I:H/A:L)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-35936
Type: osv

## Details
Pandoc is a Haskell library for converting from one markup format to another, and a command-line tool that uses this library. Starting in version 1.13 and prior to version 3.1.4, Pandoc is susceptible to an arbitrary file write vulnerability, which can be triggered by providing a specially crafted image element in the input when generating files using the `--extract-media` option or outputting to PDF format. This vulnerability allows an attacker to create or overwrite arbitrary files on the system ,depending on the privileges of the process running pandoc. It only affects systems that pass untrusted user input to pandoc and allow pandoc to be used to produce a PDF or with the `--extract-media` option.

The fix is to unescape the percent-encoding prior to checking that the resource is not above the working directory, and prior to extracting the extension.  Some code for checking that the path is below the working directory was flawed in a similar way and has also been fixed. Note that the `--sandbox` option, which only affects IO done by readers and writers themselves, does not block this vulnerability. The vulnerability is patched in pandoc 3.1.4. As a workaround, audit the pandoc command and disallow PDF output and the `--extract-media` option.

## References
- https://lists.debian.org/debian-lts-announce/2023/07/msg00029.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JGRJHU2FTSGTHHRTNDF7STEKLKKA25JN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYP3FKDS3KAYMQUZVVL73IUI4CWSKLKP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QI6RBP6ZKVC2OOCV6SU2FUHPMAXDDJFU/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35936.json
- https://github.com/jgm/pandoc/security/advisories/GHSA-xj5q-fv23-575g
- https://nvd.nist.gov/vuln/detail/CVE-2023-35936
