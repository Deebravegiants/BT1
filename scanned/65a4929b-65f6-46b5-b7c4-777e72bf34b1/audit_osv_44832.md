# [M] snipe-it before 8.7.0 Data Loss via Failed Image Write

## Summary
Severity: Medium
Advisory: CVE-2026-86749
Aliases: GHSA-v37p-hr9x-5w85
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86749
Type: osv

## Details
Snipe-IT versions <= 8.6.3 (fixed in 8.7.0) do not check the return value of storage write operations in ImageUploadRequest::handleImages(). Because Laravel's default disk mode does not throw on failure, a silently failed Storage::disk('public')->put(...) call still caused the application to delete the previous image via deleteExistingImage() and to reassign and persist the model's image reference to the new filename, destroying the existing image and leaving the database row pointing at a file that was never written. A mirror problem existed in deleteExistingImage(), where a failed Storage::delete() still nulled the model's image field, orphaning the file on disk. The condition is not directly attacker-controlled: it is triggered when any legitimate authenticated user submits an image upload while the storage backend transiently fails (for example an S3 network error, a local filesystem permission problem, or quota exhaustion). The result is unrecoverable loss of the prior image and a durable inconsistency between the database and disk that requires manual reconciliation. All models whose controllers route through ImageUploadRequest::handleImages (assets, asset models, users, companies, manufacturers, locations, categories, suppliers, departments, and other image-carrying models) are affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86749.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-v37p-hr9x-5w85
- https://nvd.nist.gov/vuln/detail/CVE-2026-86749
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-data-loss-via-failed-image-write
