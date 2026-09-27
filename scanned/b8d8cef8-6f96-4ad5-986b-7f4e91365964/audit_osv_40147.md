# [H] Oh My Zsh: Arbitrary Code Execution in oh-my-zsh dotenv plugin via malicious .env files

## Summary
Severity: High
Advisory: CVE-2026-50187
Aliases: GHSA-3rgh-p3mg-rjqg
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50187
Type: osv

## Details
Oh My Zsh is a community-driven framework for managing Zsh configuration. Prior to 2026-05-28, the dotenv plugin in plugins/dotenv/dotenv.plugin.zsh passes ZSH_DOTENV_FILE to source after a directory change into a folder containing a .env file, allowing syntactically valid shell commands in the file to execute with the current account's privileges, including without a prompt when ZSH_DOTENV_PROMPT=false or after the default prompt accepts an empty Enter response. This issue is fixed in versions released after 2026-05-28.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50187.json
- https://github.com/ohmyzsh/ohmyzsh/security/advisories/GHSA-3rgh-p3mg-rjqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-50187
- https://github.com/ohmyzsh/ohmyzsh/commit/d170d18746bb06db7b2fc97b67e281597a3fc152
- https://github.com/ohmyzsh/ohmyzsh/pull/13778
