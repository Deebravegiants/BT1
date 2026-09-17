# [M] ALPINE-CVE-2026-34978

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-34978
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34978
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.18-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, the RSS notifier allows .. path traversal in notify-recipient-uri (e.g., rss:///../job.cache), letting a remote IPP client write RSS XML bytes outside CacheDir/rss (anywhere that is lp-writable). In particular, because CacheDir is group-writable by default (typically root:lp and mode 0770), the notifier (running as lp) can replace root-managed state files via temp-file + rename(). This PoC clobbers CacheDir/job.cache with RSS XML, and after restarting cupsd the scheduler fails to parse the job cache and previously queued jobs disappear. At time of publication, there are no publicly available patches.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34978
