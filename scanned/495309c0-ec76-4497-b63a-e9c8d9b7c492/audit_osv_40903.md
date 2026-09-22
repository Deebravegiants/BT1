# [M] ALSA Library < 1.2.16.1 Double-Free via parse_def() in conf.c

## Summary
Severity: Medium
Advisory: CVE-2026-56109
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56109
Type: osv

## Details
The Advanced Linux Sound Architecture (ALSA) library before 1.2.16.1 contains a double-free vulnerability in parse_def() in src/conf.c that allows attackers to corrupt memory by supplying maliciously crafted ALSA configuration text. When parsing nested compound or array configuration blocks, parse_def() fails to check return values before continuing, causing snd_config_delete() to be called twice on the same already-freed node, resulting in a NULL-pointer write or invalid memory read.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56109.json
- https://github.com/alsa-project/alsa-lib/releases/tag/v1.2.16.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-56109
- https://www.vulncheck.com/advisories/alsa-library-double-free-via-parse-def-in-conf-c
- https://github.com/alsa-project/alsa-lib/commit/536dd6f8affdf5197c12a63a71c92a70b2833cc0
- https://github.com/alsa-project/alsa-lib
- https://lore.kernel.org/alsa-devel/CAGt8pqBU0p2voB+qHxWGcNJrKHAcBhAyHUUBPLBN-Yj_SiV6MQ@mail.gmail.com/
