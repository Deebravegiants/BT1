# [M] CVE-2020-11458

## Summary
Severity: Medium
Advisory: CVE-2020-11458
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-02
Source: https://osv.dev/vulnerability/CVE-2020-11458
Type: osv

## Details
app/Model/feed.php in MISP before 2.4.124 allows administrators to choose arbitrary files that should be ingested by MISP. This does not cause a leak of the full contents of a file, but does cause a leaks of strings that match certain patterns. Among the data that can leak are passwords from database.php or GPG key passphrases from config.php.

## References
- https://github.com/MISP/MISP/commit/30ff4b6451549dae7b526d4fb3a49061311ed477
- https://matthias.sdfeu.org/misp-poc.py
