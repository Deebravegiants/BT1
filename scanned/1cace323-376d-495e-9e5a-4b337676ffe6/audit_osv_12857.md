# [H] CVE-2018-15797

## Summary
Severity: High
Advisory: CVE-2018-15797
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/CVE-2018-15797
Type: osv

## Details
Cloud Foundry NFS volume release, 1.2.x prior to 1.2.5, 1.5.x prior to 1.5.4, 1.7.x prior to 1.7.3, logs the cf admin username and password when running the nfsbrokerpush BOSH deploy errand. A remote authenticated user with access to BOSH can obtain the admin credentials for the Cloud Foundry Platform through the logs of the NFS volume deploy errand.

## References
- https://www.cloudfoundry.org/blog/cve-2018-15797
