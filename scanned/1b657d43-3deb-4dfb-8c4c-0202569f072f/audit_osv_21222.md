# [M] CVE-2021-41190

## Summary
Severity: Medium
Advisory: CVE-2021-41190
Aliases: GHSA-mc8v-mgrf-8f4m
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2021-11-17
Source: https://osv.dev/vulnerability/CVE-2021-41190
Type: osv

## Details
The OCI Distribution Spec project defines an API protocol to facilitate and standardize the distribution of content. In the OCI Distribution Specification version 1.0.0 and prior, the Content-Type header alone was used to determine the type of document during push and pull operations. Documents that contain both “manifests” and “layers” fields could be interpreted as either a manifest or an index in the absence of an accompanying Content-Type header. If a Content-Type header changed between two pulls of the same digest, a client may interpret the resulting content differently. The OCI Distribution Specification has been updated to require that a mediaType value present in a manifest or index match the Content-Type header used during the push and pull operations. Clients pulling from a registry may distrust the Content-Type header and reject an ambiguous document that contains both “manifests” and “layers” fields or “manifests” and “config” fields if they are unable to update to version 1.0.1 of the spec.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3TUZNDAH2B26VPBK342UC3BHZNLBUXGX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4334HT7AZPLWNYHW4ARU6JBUF3VZJPZN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A2RRFNTMFYKOTRKD37F5ANMCIO3GGJML/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DX63GRWFEI5RVMYV6XLMCG4OHPWZML27/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RZTO6N55WHKHIZI4IMLY2QFBPMVTAERM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SQBCYJUIM5GVCMFUPRWKRZNXMMI5EFA4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4OJ764CKKCWCVONHD4YXTGR7HZ7LRUV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YIGVQWOA5XXCQXEOOKZX4CDAGLBDRPRX/
- http://www.openwall.com/lists/oss-security/2021/11/19/10
- https://github.com/opencontainers/distribution-spec/security/advisories/GHSA-mc8v-mgrf-8f4m
- https://github.com/opencontainers/distribution-spec/commit/ac28cac0557bcd3084714ab09f9f2356fe504923
