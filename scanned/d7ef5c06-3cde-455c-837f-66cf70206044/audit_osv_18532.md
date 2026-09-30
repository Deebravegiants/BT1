# [M] CVE-2020-28361

## Summary
Severity: Medium
Advisory: CVE-2020-28361
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-11-18
Source: https://osv.dev/vulnerability/CVE-2020-28361
Type: osv

## Details
Kamailio before 5.4.0, as used in Sip Express Router (SER) in Sippy Softswitch 4.5 through 5.2 and other products, allows a bypass of a header-removal protection mechanism via whitespace characters. This occurs in the remove_hf function in the Kamailio textops module. Particular use of remove_hf in Sippy Softswitch may allow skilled attacker having a valid credential in the system to disrupt internal call start/duration accounting mechanisms leading potentially to a loss of revenue.

## References
- https://support.sippysoft.com/support/discussions/topics/3000179616
- https://packetstormsecurity.com/files/159030/Kamailio-5.4.0-Header-Smuggling.html
