# [M] Local Blobstore may allow arbitrary reads/deletes

## Summary
Severity: Medium
Advisory: CVE-2026-41009
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:H/UI:P/VC:N/VI:H/VA:L/SC:N/SI:N/SA:L)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-41009
Type: osv

## Details
When the director sends a long-running request (e.g. compile_package), the agent's reply JSON is consumed by AgentClient. inject_compile_log (line 332-339) reads response['value']['result']['compile_log_id'] and format_exception (line 318-325) reads exception['blobstore_id']; both pass the agent-supplied string unmodified to download_and_delete_blob(blob_id) (line 344-349), which calls @resource_manager.get_resource(blob_id) and, in an ensure block, @resource_manager.delete_resource(blob_id). Api::ResourceManager forwards the id straight to blobstore.get(id) / blobstore.delete(id). When the director is configured with the local blobstore provider, Blobstore::LocalClient#object_file_path(oid) is File.join(@blobstore_path, oid) (local_client.rb:54-56) with no normalisation, so oid = "../../jobs/director/config/director.yml" resolves outside the blobstore root.

Affected versions:
BOSH Director: All versions prior to v282.1.12

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41009.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41009
- https://www.cloudfoundry.org/blog/cve-2026-41009-local-blobstore-may-allow-arbitrary-reads-deletes/
