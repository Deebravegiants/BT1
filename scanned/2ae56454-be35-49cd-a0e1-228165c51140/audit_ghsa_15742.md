# [H] yt-dlp File system modification and RCE through improper file-extension sanitization

## Summary
Severity: High
Advisory: GHSA-79w7-vh3h-8g4j
CVE: CVE-2024-38519
CWE: CWE-434, CWE-669
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-02
Source: https://github.com/advisories/GHSA-79w7-vh3h-8g4j
Type: github-advisory

## Affected
- PyPI: `yt-dlp` — affected >=0 <2024.07.01

## Details
### Summary
`yt-dlp` does not limit the extensions of downloaded files, which could lead to arbitrary filenames being created in the download folder (and path traversal on Windows). Since `yt-dlp` also reads config from the working directory (and on Windows executables will be executed from the yt-dlp directory) this could lead to arbitrary code being executed.

### Patches
`yt-dlp` version 2024.07.01 fixes this issue by whitelisting the allowed extensions.
This means some very uncommon extensions might not get downloaded; however, it will also limit the possible exploitation surface.

### Workarounds
It is recommended to upgrade yt-dlp to version 2024.07.01 as soon as possible, **always** have `.%(ext)s` at the end of the output template, and make sure you trust the websites that you are downloading from. Also, make sure to never download to a directory within PATH or other sensitive locations like your user directory, `system32`, or other binaries locations.

For users not able to upgrade:
- Make sure the extension of the media to download is a common video/audio/sub/... one
- Try to avoid the generic extractor (`--ies default,-generic`)
- Keep the default output template (`-o "%(title)s [%(id)s].%(ext)s`)
- Omit any of the subtitle options (`--write-subs`, `--write-auto-subs`, `--all-subs`, `--write-srt`)
- Use `--ignore-config --config-location ...` to not load config from common locations

### Details
One potential exploitation might look like this:

From a mimetype we do not know, we default to trimming the leading bit and using the remainder. Given a webpage that contains
```html
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": "ffmpeg",
    "encodingFormat": "video/exe",
    "contentUrl": "https://example.com/video.mp4"
}
</script>
```
this will try and download a file called `ffmpeg.exe` (`-o "%(title)s.%(ext)s`).
`ffmpeg.exe` will be searched for in the current directory, and so upon the next run arbitrary code can be executed.

Alternatively, when engineering a file called `yt-dlp.conf` to be created, the config file could contain `--exec ...` and so would also execute arbitrary code.

### Acknowledgement
A big thanks to @JarLob for independently finding a new application of the same underlying issue.
More can be read about on the dedicated GitHub Security Lab disclosure here: [Path traversal saving subtitles (GHSL-2024-090)](<https://securitylab.github.com/advisories/GHSL-2024-090_yt-dlp>)

### References
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-79w7-vh3h-8g4j
- https://nvd.nist.gov/vuln/detail/CVE-2024-38519
- https://github.com/yt-dlp/yt-dlp/releases/tag/2024.07.01
- https://github.com/yt-dlp/yt-dlp/commit/5ce582448ececb8d9c30c8c31f58330090ced03a
- https://securitylab.github.com/advisories/GHSL-2024-090_yt-dlp

## References
- https://github.com/dirkf/youtube-dl/security/advisories/GHSA-22fp-mf44-f2mq
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-79w7-vh3h-8g4j
- https://nvd.nist.gov/vuln/detail/CVE-2024-38519
- https://github.com/ytdl-org/youtube-dl/pull/32830
- https://github.com/yt-dlp/yt-dlp/commit/5ce582448ececb8d9c30c8c31f58330090ced03a
- https://github.com/ytdl-org/youtube-dl/commit/d42a222ed541b96649396ef00e19552aef0f09ec
- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp/releases/tag/2024.07.01
- https://securitylab.github.com/advisories/GHSL-2024-089_youtube-dl
- https://securitylab.github.com/advisories/GHSL-2024-090_yt-dlp
