# [M] Open edX Platform's instructor upload CSV for cohort creation not Private by Default

## Summary
Severity: Medium
Advisory: CVE-2024-41806
Aliases: GHSA-4528-7fh6-x75c
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-07-25
Source: https://osv.dev/vulnerability/CVE-2024-41806
Type: osv

## Details
The Open edX Platform is a learning management platform. Instructors can upload csv files containing learner information to create cohorts in the instructor dashboard. These files are uploaded using the django default storage. With certain storage backends, uploads may become publicly available when the uploader uses versions master, palm, olive, nutmeg, maple, lilac, koa, or juniper. The patch in commit cb729a3ced0404736dfa0ae768526c82b608657b ensures that cohorts data uploaded to AWS S3 buckets is written with a private ACL. Beyond patching, deployers should also ensure that existing cohorts uploads have a private ACL, or that other precautions are taken to avoid public access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41806.json
- https://github.com/openedx/edx-platform/security/advisories/GHSA-4528-7fh6-x75c
- https://nvd.nist.gov/vuln/detail/CVE-2024-41806
- https://github.com/openedx/edx-platform/commit/cb729a3ced0404736dfa0ae768526c82b608657b
