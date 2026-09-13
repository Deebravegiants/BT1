# [H] CVE-2025-44203

## Summary
Severity: High
Advisory: CVE-2025-44203
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-20
Source: https://osv.dev/vulnerability/CVE-2025-44203
Type: osv

## Details
In HotelDruid 3.0.7, an unauthenticated attacker can exploit verbose SQL error messages on creadb.php before the 'create database' button is pressed. By sending malformed POST requests to this endpoint, the attacker may obtain the administrator username, password hash, and salt. In some cases, the attack results in a Denial of Service (DoS), preventing the administrator from logging in even with the correct credentials.

## References
- https://www.hoteldruid.com/
- https://github.com/IvanT7D3/CVE-2025-44203/tree/main
