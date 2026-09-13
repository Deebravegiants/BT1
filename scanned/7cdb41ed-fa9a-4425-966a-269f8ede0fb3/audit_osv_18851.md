# [C] CVE-2020-36541

## Summary
Severity: Critical
Advisory: CVE-2020-36541
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-07
Source: https://osv.dev/vulnerability/CVE-2020-36541
Type: osv

## Details
A vulnerability was found in Demokratian. It has been rated as critical. Affected by this issue is some unknown functionality of the file basicos_php/genera_select.php. The manipulation of the argument id_provincia with the input -1%20union%20all%20select%201,2,3,4,database() leads to sql injection. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue.

## References
- https://vuldb.com/?id.159434
- https://alquimistadesistemas.com/sql-injection-y-archivo-peligroso-en-demokratian
- https://bitbucket.org/csalgadow/demokratian_votaciones/commits/b56c48b519fc52efa65404c312ea9bbde320e3fa
