# [H] CVE-2020-19678

## Summary
Severity: High
Advisory: CVE-2020-19678
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-06
Source: https://osv.dev/vulnerability/CVE-2020-19678
Type: osv

## Details
Directory Traversal vulnerability found in Pfsense v.2.1.3 and Pfsense Suricata v.1.4.6 pkg v.1.0.1 allows a remote attacker to obtain sensitive information via the file parameter to suricata/suricata_logs_browser.php.

## References
- http://www.2ngon.com/2015/01/lfi-vulnerability-suricata-146-pkg-v101.html
- https://github.com/pfsense/pfsense-packages/commit/59ed3438729fd56452f58a0f79f0c288db982ac3
- https://pastebin.com/8dj59053
