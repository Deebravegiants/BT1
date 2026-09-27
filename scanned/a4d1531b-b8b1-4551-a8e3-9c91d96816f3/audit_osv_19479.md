# [H] CVE-2021-21385

## Summary
Severity: High
Advisory: CVE-2021-21385
Aliases: GHSA-9657-33wf-rmvx
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-03-24
Source: https://osv.dev/vulnerability/CVE-2021-21385
Type: osv

## Details
Mifos-Mobile Android Application for MifosX is an Android Application built on top of the MifosX Self-Service platform. Mifos-Mobile before commit e505f62 disables HTTPS hostname verification of its HTTP client. Additionally it accepted any self-signed certificate as valid. Hostname verification is an important part when using HTTPS to ensure that the presented certificate is valid for the host. Disabling it can allow for man-in-the-middle attacks. Accepting any certificate, even self-signed ones allows man-in-the-middle attacks. This problem is fixed in mifos-mobile commit e505f62.

## References
- https://openmf.github.io/mobileapps.github.io/
- https://github.com/openMF/mifos-mobile/commit/e505f62b92b19292bfdabd6e996ab76abfeaa90d
- https://github.com/openMF/mifos-mobile/security/advisories/GHSA-9657-33wf-rmvx
