# [H] yt-dlp: Arbitrary code execution via manifest downloads with aria2c

## Summary
Severity: High
Advisory: GHSA-vx4q-3cr2-7cg2
CVE: CVE-2026-50574
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-vx4q-3cr2-7cg2
Type: github-advisory

## Affected
- PyPI: `yt-dlp` — affected >=0 <2026.6.9

## Details
### Summary
If aria2c is used as an external downloader for a fragmented manifest format (such as an HLS/DASH stream), yt-dlp passes insufficiently sanitized input to aria2c that allows an attacker to perform an arbitrary file write. On Windows platforms, this can lead to immediate arbitrary code execution. On non-Windows platforms, this can lead to arbitrary code execution upon the next invocation of yt-dlp.

### Details
When downloading a fragmented manifest format such as an HLS or DASH stream, yt-dlp first extracts a list of all fragment URLs from the stream's manifest. If the user has selected aria2c as an external downloader, yt-dlp then constructs an input file for aria2c from the fragment URL list and passes its filepath as the argument to aria2c's `-i` option.

aria2c's `-i` (or `--input-file`) option allows for downloading a list of URIs from the given text file. The text file must be formatted as a list of URIs separated by newlines. aria2c's format permits configuration lines for each URI, which can contain command-line options to be given to aria2c. These optional lines follow each URI line and are signified only by leading whitespace. yt-dlp constructs the input file with these optional lines so that it's able to specify the output filename for each fragment using the `out=` option.

yt-dlp's utilization of the aria2c input file format presents two known attack vectors:

1. An attacker can craft a malicious DASH manifest with one or more fragment URLs that contain `&#10;`, which is the HTML escape sequence for a newline. yt-dlp interprets this escape sequence as an actual newline character when writing the fragment URLs to the aria2c input file, which allows for an attacker to inject arbitrary aria2c options into the input file. With option injection, the attacker can achieve arbitrary file writes. This attack vector is possible only via downloads of DASH formats, since their manifests are an XML format which necessitates unescaping of HTML special characters.

2. An attacker can craft a malicious metadata response where the data parsed by yt-dlp as the `title` field (or any other metadata field that the user includes in their output template) contains strategically placed newlines and magnet URIs. If the user has passed the `--no-windows-filename` option to disable sanitization of newlines in output filenames, the attacker is able to achieve arbitrary file writes by injecting arbitrary URIs and options into the aria2c input file. This attack vector is possible via downloads of both HLS and DASH formats.

On Windows, attacker-controlled file writes can lead to immediate arbitrary code execution: the attacker could write a malicious executable file named `ffmpeg.exe` to the current working directory, and it could be invoked during the postprocessing stage if the user's `yt-dlp.exe` also resides in the current working directory.

On all platforms, attacker-controlled file writes can lead to arbitrary code execution on repeat invocations of yt-dlp: the attacker could write a yt-dlp configuration file (`yt-dlp.conf`) to the current working directory containing a malicious `--exec` argument.

### Patches
yt-dlp version 2026.06.09 fixes this issue by removing support for downloading fragmented manifest formats with aria2c.

### Workarounds
It is recommended to upgrade yt-dlp to version 2026.06.09 as soon as possible.

For users who are not able to upgrade:

- Add `--downloader dash,m3u8:native` to your yt-dlp command.

## References
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-vx4q-3cr2-7cg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-50574
- https://github.com/yt-dlp/yt-dlp/commit/25056f0d2d47adbd235a8d422fa62d68d0be2bc2
- https://github.com/advisories/GHSA-vx4q-3cr2-7cg2
- https://github.com/pypa/advisory-database/tree/main/vulns/yt-dlp/PYSEC-2026-3433.yaml
- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2026.06.09.230517
- https://github.com/yt-dlp/yt-dlp/releases/tag/2026.06.09
- https://pypi.org/project/yt-dlp
