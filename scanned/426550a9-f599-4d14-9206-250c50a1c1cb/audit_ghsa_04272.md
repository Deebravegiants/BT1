# [M] yt-dlp: File Downloader cookie leak with curl 

## Summary
Severity: Medium
Advisory: GHSA-f7j3-774f-rfhj
CVE: CVE-2026-50019
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-f7j3-774f-rfhj
Type: github-advisory

## Affected
- PyPI: `yt-dlp` — affected >=2023.9.24 <2026.6.9

## Details
### Summary
If curl is used an external downloader for yt-dlp, cookies may be leaked to an unintended host upon HTTP redirect or when the host for download fragments differs from their parent manifest's.

This is the equivalent to [GHSA-v8mc-9377-rwjj](<https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-v8mc-9377-rwjj>) for the `curl` downloader. The vulnerable behavior is present in [yt-dlp](https://github.com/yt-dlp/yt-dlp) released since 2023.09.24.

### Details
At the file download stage, the cookies are passed by yt-dlp to the file downloader via `--cookie`. However, unless these are loaded from a file, this operation does not activate the cookie engine. As a result, `curl` will send cookies with requests to domains or paths for which the cookies are not scoped.

An example of a potential attack scenario exploiting this vulnerability:
1. an attacker has crafted a malicious website with an embedded URL designed to be detected by yt-dlp as a video download. This embedded URL has the domain of a trusted site that the user has loaded cookies for, and conducts an [unvalidated redirect](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) to a target URL.
2. yt-dlp extracts this URL and calculates the cookies which are then passed to `curl`.
3. the download URL redirects to a server controlled by the attacker, to which `curl` forwards the user's sensitive cookie information.

### Patches
yt-dlp version 2026.06.09 fixes this issue by doing the following:

- Pass the cookies through stdin via `--cookie -` if `curl` is version 7.59 or higher.
- Pass the cookies via `--cookie /dev/fd/0` if the system supports this device file.
- In all other cases create a temporary file, save the cookies and then pass via `--cookie <file>`.

### Workarounds
It is recommended to upgrade yt-dlp to version 2026.06.09 as soon as possible.

For users who are not able to upgrade:

- Do not use `--downloader curl`.

## References
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-f7j3-774f-rfhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-50019
- https://github.com/yt-dlp/yt-dlp/commit/2726572520238356bcf64aba2040228648b44c82
- https://github.com/advisories/GHSA-f7j3-774f-rfhj
- https://github.com/pypa/advisory-database/tree/main/vulns/yt-dlp/PYSEC-2026-3431.yaml
- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2026.06.09.230517
- https://github.com/yt-dlp/yt-dlp/releases/tag/2026.06.09
- https://pypi.org/project/yt-dlp
