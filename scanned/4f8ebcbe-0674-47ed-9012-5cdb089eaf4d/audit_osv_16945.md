# [C] CVE-2020-10789

## Summary
Severity: Critical
Advisory: CVE-2020-10789
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-25
Source: https://osv.dev/vulnerability/CVE-2020-10789
Type: osv

## Details
openITCOCKPIT before 3.7.3 has a web-based terminal that allows attackers to execute arbitrary OS commands via shell metacharacters that are mishandled on an su command line in app/Lib/SudoMessageInterface.php.

## References
- https://openitcockpit.io/2020/2020/03/23/openitcockpit-3-7-3-released/
- https://github.com/it-novum/openITCOCKPIT/commit/73b5b34afa8bd82ff26c0097558341214c768cfc
