# [M] CVE-2021-32707

## Summary
Severity: Medium
Advisory: CVE-2021-32707
Aliases: GHSA-xxp4-44xc-8crh
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32707
Type: osv

## Details
Nextcloud Mail is a mail app for Nextcloud. In versions prior to 1.9.6, the Nextcloud Mail application does not, by default, render images in emails to not leak the read state. The privacy filter failed to filter images with a `background-image` CSS attribute. Note that the images were still passed through the Nextcloud image proxy, and thus there was no IP leakage. The issue was patched in version 1.9.6 and 1.10.0. No workarounds are known to exist.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-xxp4-44xc-8crh
- https://github.com/nextcloud/mail/pull/5189
- https://hackerone.com/reports/1215251
