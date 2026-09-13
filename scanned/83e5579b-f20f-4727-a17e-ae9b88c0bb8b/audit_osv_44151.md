# [C] TarsWeb through 3.0.16 Missing Authorization on Patch Deploy, Download and Delete Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-80348
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80348
Type: osv

## Details
TarsWeb enforces its per-application roles by calling AuthService from individual controller methods, and four methods in app/controller/patch/PatchController.js make no such call. uploadAndPublish accepts a package upload and then builds and dispatches a deployment task to every server matching the supplied application and module name, while its sibling uploadPatchPackage, which only stores the package, does check developer authorization first. The only precondition uploadAndPublish enforces is that the named server is registered, and any registered server in the installation satisfies it. downloadPackage and deletePatchPackage select a package by an unscoped sequential primary key covering every application's uploads, and setPatchPackageDefault changes which package a given application deploys by default. Any authenticated account, including one holding a role scoped to a single unrelated application, can therefore push a package to and trigger its deployment on any server the console manages, retrieve or delete any other application's package, and change which package is deployed by default.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80348.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80348
- https://www.vulncheck.com/advisories/tarsweb-through-3.0.16-missing-authorization-on-patch-deploy-download-and-delete-endpoints
- https://github.com/TarsCloud/TarsWeb/issues/213
- https://github.com/TarsCloud/TarsWeb
- https://github.com/TarsCloud/TarsWeb/blob/v3.0.16/app/controller/patch/PatchController.js
