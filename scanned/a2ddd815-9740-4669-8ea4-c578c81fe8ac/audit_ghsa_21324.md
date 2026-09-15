# [H] Powerline Gitstatus vulnerable to arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-w67g-6gjv-c599
CVE: CVE-2022-42906
CWE: CWE-77, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-13
Source: https://github.com/advisories/GHSA-w67g-6gjv-c599
Type: github-advisory

## Affected
- PyPI: `powerline-gitstatus` — affected >=0 <1.3.2

## Details
powerline-gitstatus (aka Powerline Gitstatus) before 1.3.2 allows arbitrary code execution. git repositories can contain per-repository configuration that changes the behavior of git, including running arbitrary commands. When using powerline-gitstatus, changing to a directory automatically runs git commands in order to display information about the current repository in the prompt. If an attacker can convince a user to change their current directory to one controlled by the attacker, such as in a shared filesystem or extracted archive, powerline-gitstatus will run arbitrary commands under the attacker's control. NOTE: this is similar to CVE-2022-20001.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42906
- https://github.com/jaspernbrouwer/powerline-gitstatus/issues/45
- https://github.com/jaspernbrouwer/powerline-gitstatus/commit/fe8e963b3489e4cceaa2c1f26f2bcc2ef405364c
- https://github.com/jaspernbrouwer/powerline-gitstatus
- https://github.com/jaspernbrouwer/powerline-gitstatus/releases/tag/v1.3.2
- https://lists.debian.org/debian-lts-announce/2023/01/msg00017.html
