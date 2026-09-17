# [C] Potential out-of-bound read/write in PJSIP

## Summary
Severity: Critical
Advisory: CVE-2022-24786
Aliases: GHSA-vhxv-phmx-g52q
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-06
Source: https://osv.dev/vulnerability/CVE-2022-24786
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. PJSIP versions 2.12 and prior do not parse incoming RTCP feedback RPSI (Reference Picture Selection Indication) packet, but any app that directly uses pjmedia_rtcp_fb_parse_rpsi() will be affected. A patch is available in the `master` branch of the `pjsip/pjproject` GitHub repository. There are currently no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24786.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-vhxv-phmx-g52q
- https://nvd.nist.gov/vuln/detail/CVE-2022-24786
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/11559e49e65bdf00922ad5ae28913ec6a198d508
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
