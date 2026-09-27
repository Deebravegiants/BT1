# [M] Secret logging may occur in debug mode of Atlas Operator

## Summary
Severity: Medium
Advisory: CVE-2023-0436
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-11-07
Source: https://osv.dev/vulnerability/CVE-2023-0436
Type: osv

## Details
The affected versions of MongoDB Atlas Kubernetes Operator may print sensitive information like GCP service account keys and API integration secrets while DEBUG mode logging is enabled. This issue affects MongoDB Atlas Kubernetes Operator versions: 1.5.0, 1.6.0, 1.6.1, 1.7.0.

Please note that this is reported on an EOL version of the product, and users are advised to upgrade to the latest supported version.
Required Configuration: 

DEBUG logging is not enabled by default, and must be configured by the end-user. To check the log-level of the Operator, review the flags passed in your deployment configuration (eg.  https://github.com/mongodb/mongodb-atlas-kubernetes/blob/main/config/manager/manager.yaml#L27 https://github.com/mongodb/mongodb-atlas-kubernetes/blob/main/config/manager/manager.yaml#L27 )

## References
- https://github.com/mongodb/mongodb-atlas-kubernetes/releases/tag/v1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0436.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0436
