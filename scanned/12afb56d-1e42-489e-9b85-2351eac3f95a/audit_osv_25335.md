# [M] Thruk has Path Traversal Vulnerability in panorama.pm

## Summary
Severity: Medium
Advisory: CVE-2023-34096
Aliases: GHSA-vhqc-649h-994h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-34096
Type: osv

## Details
Thruk is a multibackend monitoring webinterface which currently supports Naemon, Icinga, Shinken and Nagios as backends. In versions 3.06 and prior, the file `panorama.pm` is vulnerable to a Path Traversal vulnerability which allows an attacker to upload a file to any folder which has write permissions on the affected system. The parameter location is not filtered, validated or sanitized and it accepts any kind of characters. For a path traversal attack, the only characters required were the dot (`.`) and the slash (`/`). A fix is available in version 3.06.2.

## References
- http://packetstormsecurity.com/files/172822/Thruk-Monitoring-Web-Interface-3.06-Path-Traversal.html
- https://github.com/sni/Thruk/blob/1bc5a5804bf9fc22e82a4eadb21a1795954f0867/plugins/plugins-available/panorama/lib/Thruk/Controller/panorama.pm#L690
- https://github.com/sni/Thruk/blob/1bc5a5804bf9fc22e82a4eadb21a1795954f0867/plugins/plugins-available/panorama/lib/Thruk/Controller/panorama.pm#L705
- https://github.com/sni/Thruk/blob/1bc5a5804bf9fc22e82a4eadb21a1795954f0867/plugins/plugins-available/panorama/lib/Thruk/Controller/panorama.pm#L727
- https://github.com/sni/Thruk/blob/1bc5a5804bf9fc22e82a4eadb21a1795954f0867/plugins/plugins-available/panorama/lib/Thruk/Controller/panorama.pm#L735
- https://www.exploit-db.com/exploits/51509
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34096.json
- https://github.com/sni/Thruk/security/advisories/GHSA-vhqc-649h-994h
- https://nvd.nist.gov/vuln/detail/CVE-2023-34096
- https://github.com/sni/Thruk/commit/26de047275c355c5ae2bbbc51b164f0f8bef5c5b
- https://github.com/sni/Thruk/commit/cf03f67621b7bb20e2c768bc62b30e976206aa17
- https://github.com/galoget/Thruk-CVE-2023-34096
- https://galogetlatorre.blogspot.com/2023/06/cve-2023-34096-path-traversal-thruk.html
