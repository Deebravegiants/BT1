# [M] CVE-2018-3979

## Summary
Severity: Medium
Advisory: CVE-2018-3979
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-01
Source: https://osv.dev/vulnerability/CVE-2018-3979
Type: osv

## Details
A remote denial-of-service vulnerability exists in the way the Nouveau Display Driver (the default Ubuntu Nvidia display driver) handles GPU shader execution. A specially crafted pixel shader can cause remote denial-of-service issues. An attacker can provide a specially crafted website to trigger this vulnerability. This vulnerability can be triggered remotely after the user visits a malformed website. No further user interaction is required. Vulnerable versions include Ubuntu 18.04 LTS (linux 4.15.0-29-generic x86_64), Nouveau Display Driver NV117 (vermagic: 4.15.0-29-generic SMP mod_unload).

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2018-0647
