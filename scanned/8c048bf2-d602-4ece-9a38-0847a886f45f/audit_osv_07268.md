# [C] BIT-phplist-2020-22249

## Summary
Severity: Critical
Advisory: BIT-phplist-2020-22249
Aliases: CVE-2020-22249
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-phplist-2020-22249
Type: osv

## Affected
- Bitnami: `phplist` — affected >=3.5.1

## Details
Remote Code Execution vulnerability in phplist 3.5.1. The application does not check any file extensions stored in the plugin zip file, Uploading a malicious plugin which contains the php files with extensions like PHP,phtml,php7 will be copied to the plugins directory which would lead to the remote code execution

## References
- https://drive.google.com/open?id=1znDU4fDKA_seg16mJLLtgaaFfvmf-mS6
