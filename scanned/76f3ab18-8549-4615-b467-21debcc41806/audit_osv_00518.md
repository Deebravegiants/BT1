# [H] ALPINE-CVE-2017-14500

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14500
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14500
Type: osv

## Affected
- Alpine:v3.3: `newsbeuter` — affected >=0 <2.9-r5
- Alpine:v3.4: `newsbeuter` — affected >=0 <2.9-r5
- Alpine:v3.5: `newsbeuter` — affected >=0 <2.9-r5
- Alpine:v3.6: `newsbeuter` — affected >=0 <2.9-r5
- Alpine:v3.7: `newsbeuter` — affected >=0 <2.9-r5

## Details
Improper Neutralization of Special Elements used in an OS Command in the podcast playback function of Podbeuter in Newsbeuter 0.3 through 2.9 allows remote attackers to perform user-assisted code execution by crafting an RSS item with a media enclosure (i.e., a podcast file) that includes shell metacharacters in its filename, related to pb_controller.cpp and queueloader.cpp, a different vulnerability than CVE-2017-12904.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14500
