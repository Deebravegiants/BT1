# [M] cups-browsed binds to `INADDR_ANY:631`, trusting any packet from any source

## Summary
Severity: Medium
Advisory: CVE-2024-47176
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/CVE-2024-47176
Type: osv

## Details
CUPS is a standards-based, open-source printing system, and `cups-browsed` contains network printing functionality including, but not limited to, auto-discovering print services and shared printers. `cups-browsed` binds to `INADDR_ANY:631`, causing it to trust any packet from any source, and can cause the `Get-Printer-Attributes` IPP request to an attacker controlled URL. When combined with other vulnerabilities, such as CVE-2024-47076, CVE-2024-47175, and CVE-2024-47177, an attacker can execute arbitrary commands remotely on the target machine without authentication when a malicious printer is printed to.

## References
- http://www.openwall.com/lists/oss-security/2024/09/27/6
- http://www.openwall.com/lists/oss-security/2025/09/11/2
- https://github.com/OpenPrinting/cups-browsed/blob/master/daemon/cups-browsed.c#L13992
- https://lists.debian.org/debian-lts-announce/2024/09/msg00048.html
- https://www.cups.org
- https://www.evilsocket.net/2024/09/26/Attacking-UNIX-systems-via-CUPS-Part-I
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47176.json
- https://github.com/OpenPrinting/cups-browsed/security/advisories/GHSA-rj88-6mr5-rcw8
- https://github.com/OpenPrinting/cups-filters/security/advisories/GHSA-p9rh-jxmq-gq47
- https://github.com/OpenPrinting/libcupsfilters/security/advisories/GHSA-w63j-6g73-wmg5
- https://github.com/OpenPrinting/libppd/security/advisories/GHSA-7xfx-47qg-grp6
- https://nvd.nist.gov/vuln/detail/CVE-2024-47176
- https://security.netapp.com/advisory/ntap-20241011-0001/
- https://github.com/OpenPrinting/cups-browsed/commit/1debe6b140c37e0aa928559add4abcc95ce54aa2
