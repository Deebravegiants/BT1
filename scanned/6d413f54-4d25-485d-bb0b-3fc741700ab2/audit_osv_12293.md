# [H] CVE-2018-11243

## Summary
Severity: High
Advisory: CVE-2018-11243
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-18
Source: https://osv.dev/vulnerability/CVE-2018-11243
Type: osv

## Details
PackLinuxElf64::unpack in p_lx_elf.cpp in UPX 3.95 allows remote attackers to cause a denial of service (double free), limit the ability of a malware scanner to operate on the entire original data, or possibly have unspecified other impact via a crafted file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00008.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D7XU42G6MUQQXHWRP7DCF2JSIBOJ5GOO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EUTVSTXAFTD552NO2K2RIF6MDQEHP3BE/
- https://github.com/upx/upx/blob/devel/NEWS
- https://github.com/upx/upx/issues/206
- https://github.com/upx/upx/issues/207
