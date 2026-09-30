# [M] CVE-2017-8761

## Summary
Severity: Medium
Advisory: CVE-2017-8761
Aliases: GHSA-8fxc-qm65-vpxg, PYSEC-2026-751
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2017-8761
Type: osv

## Details
In OpenStack Swift through 2.10.1, 2.11.0 through 2.13.0, and 2.14.0, the proxy-server logs full tempurl paths, potentially leaking reusable tempurl signatures to anyone with read access to these logs. All Swift deployments using the tempurl middleware are affected.

## References
- https://launchpad.net/bugs/1685798
