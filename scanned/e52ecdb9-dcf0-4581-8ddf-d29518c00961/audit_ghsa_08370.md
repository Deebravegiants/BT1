# [H] Authenticated Sharp users can download unrelated Laravel Storage objects through the generic download endpoint

## Summary
Severity: High
Advisory: GHSA-748w-hm6r-qc7v
CVE: CVE-2026-44692
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-748w-hm6r-qc7v
Type: github-advisory

## Affected
- Packagist: `code16/sharp` — affected >=0 <9.22.0

## Details
Sharp exposes a generic download endpoint that authorizes access only to the supplied Sharp entity instance, but then reads the target storage `disk` and `path` from request parameters.

Because the requested storage object is not bound to the authorized entity instance, an authenticated Sharp user who can view one valid record may use that record as an authorization anchor to download unrelated disk-relative objects from configured Laravel Storage disks.

The confirmed impact is authenticated disclosure of unrelated objects from configured Laravel Storage disks. This issue does not imply arbitrary host filesystem access outside configured Laravel Storage disk roots.

### Impact

An authenticated Sharp user with view access to at least one valid Sharp entity instance may be able to download unrelated files from configured Laravel Storage disks by supplying a different `disk` and `path` to the generic download endpoint.

Depending on the application, exposed files may include exports, backups, invoices, internal documents, uploads belonging to other records, tenant-specific data, or operational files stored on private application disks.

The attacker does not need authorization to the storage object being downloaded. They only need an authenticated Sharp session and view access to one valid entity instance that can be used as the authorization anchor.

### Attack requirements

An attacker must have:

- an authenticated Sharp session
- view access to at least one valid Sharp entity instance

The attacker does not need authorization to the storage object being downloaded.

### Affected endpoint

`GET /sharp/{globalFilter}/download/{entityKey}/{instanceId?}`

### Patches

After the fix, requests to the generic download endpoint without a valid signature are rejected. Modifying the `disk`, `path`, `entityKey`, or `instanceId` parameters of a Sharp-generated download URL invalidates the signature and prevents the modified request from being used to download another storage object.

### Workarounds

If upgrading is not immediately possible, applications should restrict `downloads.allowed_disks` to the smallest possible set of disks required by Sharp downloads.

Applications should also avoid storing sensitive unrelated files on disks reachable by Sharp’s generic download endpoint, and should add application-level controls to ensure that requested files are bound to the authorized record.

Disk allowlisting reduces the reachable storage surface, but it does not fully fix the missing per-record file binding. Upgrading to a patched version is recommended.

### Resources

- Laravel signed URLs documentation: https://laravel.com/docs/urls#signed-urls
- CWE-639: https://cwe.mitre.org/data/definitions/639.html

## References
- https://github.com/code16/sharp/security/advisories/GHSA-748w-hm6r-qc7v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44692
- https://github.com/code16/sharp
- https://github.com/code16/sharp/releases/tag/v9.22.0
