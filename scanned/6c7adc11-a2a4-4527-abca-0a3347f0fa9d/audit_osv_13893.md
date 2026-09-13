# [H] CVE-2018-3836

## Summary
Severity: High
Advisory: CVE-2018-3836
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2018-3836
Type: osv

## Details
An exploitable command injection vulnerability exists in the gplotMakeOutput function of Leptonica 1.74.4. A specially crafted gplot rootname argument can cause a command injection resulting in arbitrary code execution. An attacker can provide a malicious path as input to an application that passes attacker data to this function to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2018/02/msg00019.html
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2018-0516
