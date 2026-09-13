# [H] CVE-2020-7982

## Summary
Severity: High
Advisory: CVE-2020-7982
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2020-7982
Type: osv

## Details
An issue was discovered in OpenWrt 18.06.0 to 18.06.6 and 19.07.0, and LEDE 17.01.0 to 17.01.7. A bug in the fork of the opkg package manager before 2020-01-25 prevents correct parsing of embedded checksums in the signed repository index, allowing a man-in-the-middle attacker to inject arbitrary package payloads (which are installed without verification).

## References
- https://openwrt.org/advisory/2020-01-31-1
- https://github.com/openwrt/openwrt/commits/master
- https://arstechnica.com/information-technology/2020/03/openwrt-is-vulnerable-to-attacks-that-execute-malicious-code/
- https://blog.forallsecure.com/uncovering-openwrt-remote-code-execution-cve-2020-7982
