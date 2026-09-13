# [H] CVE-2024-42040

## Summary
Severity: High
Advisory: CVE-2024-42040
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-08-23
Source: https://osv.dev/vulnerability/CVE-2024-42040
Type: osv

## Details
Buffer Overflow vulnerability in the net/bootp.c in DENEX U-Boot from its initial commit in 2002 (3861aa5) up to today on any platform allows an attacker on the local network to leak memory from four up to 32 bytes of memory stored behind the packet to the network depending on the later use of DHCP-provided parameters via crafted DHCP responses.

## References
- http://seclists.org/fulldisclosure/2024/Aug/38
- https://github.com/u-boot/u-boot/tags
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42040.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42040
- https://www.schutzwerk.com/advisories/SCHUTZWERK-SA-2024-004.txt
