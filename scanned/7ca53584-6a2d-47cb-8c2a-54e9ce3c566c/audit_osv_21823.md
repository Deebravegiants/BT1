# [H] CVE-2021-46850

## Summary
Severity: High
Advisory: CVE-2021-46850
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-24
Source: https://osv.dev/vulnerability/CVE-2021-46850
Type: osv

## Details
myVesta Control Panel before 0.9.8-26-43 and Vesta Control Panel before 0.9.8-26 are vulnerable to command injection. An authenticated and remote administrative user can execute arbitrary commands via the v_sftp_license parameter when sending HTTP POST requests to the /edit/server endpoint.

## References
- https://github.com/myvesta/vesta/releases/tag/0.9.8-26-43
- https://github.com/myvesta/vesta/commit/7991753ab7c5c568768028fb77554db8ea149f17
- https://github.com/serghey-rodin/vesta/commit/a4e4542a6d1351c2857b169f8621dd9a13a2e896
- https://blog.talosintelligence.com/2021/06/necro-python-bot-adds-new-tricks.html
- https://www.exploit-db.com/exploits/49674
