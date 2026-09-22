# [C] CVE-2018-1000871

## Summary
Severity: Critical
Advisory: CVE-2018-1000871
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000871
Type: osv

## Details
HotelDruid HotelDruid 2.3.0 version 2.3.0 and earlier contains a SQL Injection vulnerability in "id_utente_mod" parameter in gestione_utenti.php file that can result in An attacker can dump all the database records of backend webserver. This attack appear to be exploitable via the attack can be done by anyone via specially crafted sql query passed to the "id_utente_mod=1" parameter.

## References
- https://www.exploit-db.com/exploits/45976
