# [H] unzip-bot Allows Remote Code Execution (RCE) via archive extraction, password prompt, or video upload

## Summary
Severity: High
Advisory: CVE-2024-53992
Aliases: GHSA-34cg-7f8c-fm5h
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53992
Type: osv

## Details
unzip-bot is a Telegram bot to extract various types of archives. Users could exploit unsanitized inputs to inject malicious commands that are executed through subprocess.Popen with shell=True. Attackers can exploit this vulnerability using a crafted archive name, password, or video name. This vulnerability is fixed in 7.0.3a.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53992.json
- https://github.com/EDM115/unzip-bot/security/advisories/GHSA-34cg-7f8c-fm5h
- https://nvd.nist.gov/vuln/detail/CVE-2024-53992
- https://github.com/EDM115/unzip-bot/commit/5213b693eabb562842cdbf21c1074e91bfa00274
