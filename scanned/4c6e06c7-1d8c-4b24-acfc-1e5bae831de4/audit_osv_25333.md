# [H] ChuanhuChatGPT vulnerable to unauthorized configuration file access

## Summary
Severity: High
Advisory: CVE-2023-34094
Aliases: GHSA-j34w-9xr4-m9p8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-34094
Type: osv

## Details
ChuanhuChatGPT is a graphical user interface for ChatGPT and many large language models. A vulnerability in versions 20230526 and prior allows unauthorized access to the config.json file of the privately deployed ChuanghuChatGPT project, when authentication is not configured. The attacker can exploit this vulnerability to steal the API keys in the configuration file. The vulnerability has been fixed in commit bfac445. As a workaround, setting up access authentication can help mitigate the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34094.json
- https://github.com/GaiZhenbiao/ChuanhuChatGPT/security/advisories/GHSA-j34w-9xr4-m9p8
- https://nvd.nist.gov/vuln/detail/CVE-2023-34094
- https://github.com/GaiZhenbiao/ChuanhuChatGPT/commit/bfac445e799c317b0f5e738ab394032a18de62eb
