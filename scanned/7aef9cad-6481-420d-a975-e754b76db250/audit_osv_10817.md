# [H] CVE-2017-2902

## Summary
Severity: High
Advisory: CVE-2017-2902
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-2902
Type: osv

## Details
An exploitable integer overflow exists in the DPX loading functionality of the Blender open-source 3d creation suite version 2.78c. A specially crafted '.cin' file can cause an integer overflow resulting in a buffer overflow which can allow for code execution under the context of the application. An attacker can convince a user to use the file as an asset via the sequencer in order to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00011.html
- https://www.debian.org/security/2018/dsa-4248
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0409
