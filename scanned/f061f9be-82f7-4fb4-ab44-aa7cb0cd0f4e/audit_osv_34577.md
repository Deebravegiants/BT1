# [M] CVE-2025-62185

## Summary
Severity: Medium
Advisory: CVE-2025-62185
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2025-62185
Type: osv

## Details
In Ankitects Anki before 25.02.5, a crafted shared deck can place a YouTube downloader executable in the media folder, and this is executed for a YouTube link in the deck. The executable name could be youtube-dl.exe or yt-dlp.exe or yt-dlp_x86.exe.

## References
- https://github.com/ankitects/anki/compare/25.02.4...25.02.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62185.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-62185
- https://github.com/ankitects/anki/commit/5080451829505842b16d4a50f398ad44560a3e48
- https://github.com/ankitects/anki/commit/6213c9b6f99ebda181004f8915b92fe3618b939
