# [M] Libssh: out-of-bounds read in sftp_handle()

## Summary
Severity: Medium
Advisory: CVE-2025-5318
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-5318
Type: osv

## Details
A flaw was found in the libssh library in versions less than 0.11.2. An out-of-bounds read can be triggered in the sftp_handle function due to an incorrect comparison check that permits the function to access memory beyond the valid handle list and to return an invalid pointer, which is used in further processing. This vulnerability allows an authenticated remote attacker to potentially read unintended memory regions, exposing sensitive information or affect service behavior.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://www.libssh.org/
- https://access.redhat.com/errata/RHSA-2025:18231
- https://access.redhat.com/errata/RHSA-2025:18275
- https://access.redhat.com/errata/RHSA-2025:18286
- https://access.redhat.com/errata/RHSA-2025:19012
- https://access.redhat.com/errata/RHSA-2025:19098
- https://access.redhat.com/errata/RHSA-2025:19101
- https://access.redhat.com/errata/RHSA-2025:19295
- https://access.redhat.com/errata/RHSA-2025:19300
- https://access.redhat.com/errata/RHSA-2025:19313
- https://access.redhat.com/errata/RHSA-2025:19400
- https://access.redhat.com/errata/RHSA-2025:19401
- https://access.redhat.com/errata/RHSA-2025:19470
- https://access.redhat.com/errata/RHSA-2025:19472
- https://access.redhat.com/errata/RHSA-2025:19807
- https://access.redhat.com/errata/RHSA-2025:19864
- https://access.redhat.com/errata/RHSA-2025:20943
- https://access.redhat.com/errata/RHSA-2025:21013
