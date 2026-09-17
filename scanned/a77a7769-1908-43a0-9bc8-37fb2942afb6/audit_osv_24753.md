# [H] ZoneMinder contains Local File Inclusion vulnerability

## Summary
Severity: High
Advisory: CVE-2023-26036
Aliases: GHSA-h5m9-6jjc-cgmw
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26036
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application for Linux which supports IP, USB and Analog cameras. Versions prior to 1.36.33 and 1.37.33 contain a Local File Inclusion (Untrusted Search Path) vulnerability via /web/index.php. By controlling $view, any local file ending in .php can be executed. This is supposed to be mitigated by calling detaintPath, however dentaintPath does not properly sandbox the path. This can be exploited by constructing paths like "..././", which get replaced by "../". This issue is patched in versions 1.36.33 and 1.37.33.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26036.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-h5m9-6jjc-cgmw
- https://nvd.nist.gov/vuln/detail/CVE-2023-26036
