# [C] LocalAI Command Injection in audioToWav

## Summary
Severity: Critical
Advisory: GHSA-wx43-g55g-2jf4
CVE: CVE-2024-2029
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-wx43-g55g-2jf4
Type: github-advisory

## Affected
- Go: `github.com/go-skynet/LocalAI` — affected >=0 <2.10.0

## Details
A command injection vulnerability exists in the `TranscriptEndpoint` of mudler/localai, specifically within the `audioToWav` function used for converting audio files to WAV format for transcription. The vulnerability arises due to the lack of sanitization of user-supplied filenames before passing them to ffmpeg via a shell command, allowing an attacker to execute arbitrary commands on the host system. Successful exploitation could lead to unauthorized access, data breaches, or other detrimental impacts, depending on the privileges of the process executing the code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2029
- https://github.com/mudler/localai/commit/31a4c9c9d3abc58de2bdc5305419181c8b33eb1c
- https://github.com/mudler/LocalAI
- https://huntr.com/bounties/e092528a-ce3b-4e66-9b98-3f56d6b276b0
