# [C] CVE-2022-46387

## Summary
Severity: Critical
Advisory: CVE-2022-46387
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/CVE-2022-46387
Type: osv

## Details
ConEmu through 220807 and Cmder before 1.3.21 report the title of the terminal, including control characters, which allows an attacker to change the title and then execute it as commands.

## References
- https://gist.github.com/dgl/05ca60cdc7efc9e47bbc58d0c952635e
- https://github.com/cmderdev/cmder/blob/master/CHANGELOG.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46387.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46387
