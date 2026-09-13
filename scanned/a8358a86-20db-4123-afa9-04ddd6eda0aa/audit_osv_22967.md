# [H] CVE-2022-41751

## Summary
Severity: High
Advisory: CVE-2022-41751
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-41751
Type: osv

## Details
Jhead 3.06.0.1 allows attackers to execute arbitrary OS commands by placing them in a JPEG filename and then using the regeneration -rgt50 option.

## References
- https://github.com/Matthias-Wandel/jhead/blob/63ce118c6a59ea64ac357236a11a47aaf569d622/jhead.c#L788
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41751.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5NM6FET4ZNWV4EQGKZTLZFWTNVODGVOK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EG26AD7KJAY5B6L6OERSGL4FRXJE3GOB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TAVB3ZX7E5ULEXESU5NXZIAHY6CVGCHB/
- https://nvd.nist.gov/vuln/detail/CVE-2022-41751
- https://www.debian.org/security/2022/dsa-5294
- https://github.com/Matthias-Wandel/jhead/pull/57
- https://github.com/Matthias-Wandel/jhead
- https://lists.debian.org/debian-lts-announce/2022/12/msg00004.html
