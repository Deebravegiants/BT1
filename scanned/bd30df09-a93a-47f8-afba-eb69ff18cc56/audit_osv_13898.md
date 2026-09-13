# [H] CVE-2018-3968

## Summary
Severity: High
Advisory: CVE-2018-3968
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2018-3968
Type: osv

## Details
An exploitable vulnerability exists in the verified boot protection of the Das U-Boot from version 2013.07-rc1 to 2014.07-rc2. The affected versions lack proper FIT signature enforcement, which allows an attacker to bypass U-Boot's verified boot and execute an unsigned kernel, embedded in a legacy image format. To trigger this vulnerability, a local attacker needs to be able to supply the image to boot.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2018-0633
