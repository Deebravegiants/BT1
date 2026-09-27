# [H] CVE-2018-6513

## Summary
Severity: High
Advisory: CVE-2018-6513
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-6513
Type: osv

## Details
Puppet Enterprise 2016.4.x prior to 2016.4.12, Puppet Enterprise 2017.3.x prior to 2017.3.7, Puppet Enterprise 2018.1.x prior to 2018.1.1, Puppet Agent 1.10.x prior to 1.10.13, Puppet Agent 5.3.x prior to 5.3.7, and Puppet Agent 5.5.x prior to 5.5.2, were vulnerable to an attack where an unprivileged user on Windows agents could write custom facts that can escalate privileges on the next puppet run. This was possible through the loading of shared libraries from untrusted paths.

## References
- https://puppet.com/security/cve/CVE-2018-6513
