# [M] Compromised VM can make arbitrary blobstore deletes

## Summary
Severity: Medium
Advisory: CVE-2026-41704
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-41704
Type: osv

## Details
AgentClient#handle_method (lines 264-303) processes every NATS reply. It calls inject_compile_log (line 273) on every response, which reads response['value']['result']['compile_log_id'] (line 332-338) and passes it to download_and_delete_blob. Separately, any response containing 'exception' goes through format_exception (lines 308-325), which reads exception['blobstore_id'] and also calls download_and_delete_blob. That helper (lines 344-349) calls ResourceManager#get_resource(blob_id) and, in an ensure block, ResourceManager#delete_resource(blob_id). ResourceManager (resource_manager.rb:62-70) calls blobstore.delete(id) on the single shared Director blobstore with no UUID-format check, no ownership check, and no namespace prefix.

Affected versions:
BOSH Director: All versions prior to v282.1.12

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41704.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41704
- https://www.cloudfoundry.org/blog/cve-2026-41704-compromised-vm-can-make-arbitrary-blobstore-deletes/
