# [H] BIT-abantecart-2022-26521

## Summary
Severity: High
Advisory: BIT-abantecart-2022-26521
Aliases: CVE-2022-26521
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-abantecart-2022-26521
Type: osv

## Affected
- Bitnami: `abantecart` — affected >=0 <1.3.2

## Details
Abantecart through 1.3.2 allows remote authenticated administrators to execute arbitrary code by uploading an executable file, because the Catalog>Media Manager>Images settings can be changed by an administrator (e.g., by configuring .php to be a valid image file type).

## References
- http://packetstormsecurity.com/files/171487/Abantecart-1.3.2-Remote-Code-Execution.html
- https://github.com/sartlabs/0days/blob/main/Abantecart/Exploit.txt
