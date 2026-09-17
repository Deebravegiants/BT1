# [M] CVE-2019-6474

## Summary
Severity: Medium
Advisory: CVE-2019-6474
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/CVE-2019-6474
Type: osv

## Details
A missing check on incoming client requests can be exploited to cause a situation where the Kea server's lease storage contains leases which are rejected as invalid when the server tries to load leases from storage on restart. If the number of such leases exceeds a hard-coded limit in the Kea code, a server trying to restart will conclude that there is a problem with its lease store and give up. Versions affected: 1.4.0 to 1.5.0, 1.6.0-beta1, and 1.6.0-beta2

## References
- https://kb.isc.org/docs/cve-2019-6474
