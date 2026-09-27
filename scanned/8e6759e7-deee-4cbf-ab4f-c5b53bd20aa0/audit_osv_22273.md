# [H] Potential infinite loop when parsing WAV format file in PJSIP

## Summary
Severity: High
Advisory: CVE-2022-24792
Aliases: GHSA-rwgw-vwxg-q799
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-25
Source: https://osv.dev/vulnerability/CVE-2022-24792
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. A denial-of-service vulnerability affects applications on a 32-bit systems that use PJSIP versions 2.12 and prior to play/read invalid WAV files. The vulnerability occurs when reading WAV file data chunks with length greater than 31-bit integers. The vulnerability does not affect 64-bit apps and should not affect apps that only plays trusted WAV files. A patch is available on the `master` branch of the `pjsip/project` GitHub repository. As a workaround, apps can reject a WAV file received from an unknown source or validate the file first.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24792.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-rwgw-vwxg-q799
- https://nvd.nist.gov/vuln/detail/CVE-2022-24792
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/947bc1ee6d05be10204b918df75a503415fd3213
- https://lists.debian.org/debian-lts-announce/2022/05/msg00047.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
