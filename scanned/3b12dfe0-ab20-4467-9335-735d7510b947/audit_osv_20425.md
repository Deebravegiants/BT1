# [H] CVE-2021-33525

## Summary
Severity: High
Advisory: CVE-2021-33525
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-24
Source: https://osv.dev/vulnerability/CVE-2021-33525
Type: osv

## Details
EyesOfNetwork eonweb through 5.3-11 allows Remote Command Execution (by authenticated users) via shell metacharacters in the nagios_path parameter to lilac/export.php, as demonstrated by %26%26+curl to insert an "&& curl" substring for the shell.

## References
- https://github.com/EyesOfNetworkCommunity/eonweb/releases
- https://github.com/ArianeBlow/LilacPathVUln/blob/main/eon-pwn.sh
