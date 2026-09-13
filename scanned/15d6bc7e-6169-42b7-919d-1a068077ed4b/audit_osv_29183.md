# [H] CVE-2024-40897

## Summary
Severity: High
Advisory: CVE-2024-40897
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-26
Source: https://osv.dev/vulnerability/CVE-2024-40897
Type: osv

## Details
Stack-based buffer overflow vulnerability exists in orcparse.c of ORC versions prior to 0.4.39. If a developer is tricked to process a specially crafted file with the affected ORC compiler, an arbitrary code may be executed on the developer's build environment. This may lead to compromise of developer machines or CI build environments.

## References
- http://www.openwall.com/lists/oss-security/2024/07/26/1
- https://gstreamer.freedesktop.org/modules/orc.html
- https://jvn.jp/en/jp/JVN02030803/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40897.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40897
- https://github.com/GStreamer/orc
