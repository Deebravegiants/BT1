# [C] CVE-2023-24258

## Summary
Severity: Critical
Advisory: CVE-2023-24258
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-27
Source: https://osv.dev/vulnerability/CVE-2023-24258
Type: osv

## Details
SPIP v4.1.5 and earlier was discovered to contain a SQL injection vulnerability via the _oups parameter. This vulnerability allows attackers to execute arbitrary code via a crafted POST request.

## References
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-1-7-SPIP-4-0-9-et-SPIP-3-2-17.html
- https://www.debian.org/security/2023/dsa-5325
- https://github.com/Abyss-W4tcher/ab4yss-wr4iteups/blob/ffa980faa9e3598d49d6fb7def4f7a67cfb5f427/SPIP%20-%20Pentest/SPIP%204.1.5/SPIP_4.1.5_AND_BEFORE_AUTH_SQLi_Abyss_Watcher.md
