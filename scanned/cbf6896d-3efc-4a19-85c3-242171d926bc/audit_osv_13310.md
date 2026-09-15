# [C] CVE-2018-19168

## Summary
Severity: Critical
Advisory: CVE-2018-19168
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-11
Source: https://osv.dev/vulnerability/CVE-2018-19168
Type: osv

## Details
Shell Metacharacter Injection in www/modules/save.php in FruityWifi (aka PatatasFritas/PatataWifi) through 2.4 allows remote attackers to execute arbitrary code with root privileges via a crafted mod_name parameter in a POST request. NOTE: unlike in CVE-2018-17317, the attacker does not need a valid session.

## References
- https://github.com/xtr4nge/FruityWifi/issues/250
