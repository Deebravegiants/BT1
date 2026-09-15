# [C] CAT through 3.1.0 Session Cookie Forgery via Unkeyed hashCode Checksum

## Summary
Severity: Critical
Advisory: CVE-2026-85181
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85181
Type: osv

## Details
CAT uses Java String.hashCode as the sole integrity check for session cookies without server-side keying, allowing attackers to forge valid checksums offline. Attackers can set the x-forwarded-for header to bypass IP binding validation and create admin sessions with full configuration access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85181.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85181
- https://www.vulncheck.com/advisories/cat-through-3.1.0-session-cookie-forgery-via-unkeyed-hashcode-checksum
- https://github.com/dianping/cat/issues/2384
- https://github.com/dianping/cat
- https://github.com/dianping/cat/blob/3.1.0/cat-home/src/main/java/com/dianping/cat/system/page/login/service/TokenBuilder.java
- https://github.com/dianping/cat/blob/3.1.0/cat-home/src/main/java/com/dianping/cat/util/HttpUtils.java
