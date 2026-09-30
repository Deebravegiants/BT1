# [H] CVE-2020-7058

## Summary
Severity: High
Advisory: CVE-2020-7058
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-15
Source: https://osv.dev/vulnerability/CVE-2020-7058
Type: osv

## Details
data_input.php in Cacti 1.2.8 allows remote code execution via a crafted Input String to Data Collection -> Data Input Methods -> Unix -> Ping Host. NOTE: the vendor has stated "This is a false alarm.

## References
- https://github.com/Cacti/cacti/issues/3186
