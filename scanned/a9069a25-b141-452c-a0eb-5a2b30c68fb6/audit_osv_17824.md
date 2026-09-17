# [H] CVE-2020-20444

## Summary
Severity: High
Advisory: CVE-2020-20444
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-16
Source: https://osv.dev/vulnerability/CVE-2020-20444
Type: osv

## Details
Jact OpenClinic 0.8.20160412 allows the attacker to read server files after login to the the admin account by an infected 'file' GET parameter in '/shared/view_source.php' which "could" lead to RCE vulnerability .

## References
- https://github.com/jact/openclinic/issues/8
- https://cwe.mitre.org/data/definitions/23.html
