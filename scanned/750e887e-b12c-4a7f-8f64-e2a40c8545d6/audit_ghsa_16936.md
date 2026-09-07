# [H] Rancher does not properly specify ApiGroup when creating Kubernetes RBAC resources

## Summary
Severity: High
Advisory: GHSA-f9xf-jq4j-vqw4
CVE: CVE-2021-25318
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-f9xf-jq4j-vqw4
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0 <2.4.16
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.9

## Details
A vulnerability was discovered in Rancher versions 2.0 through the aforementioned fixed versions, where users were granted access to resources regardless of the resource's API group. For example Rancher should have allowed users access to `apps.catalog.cattle.io`, but instead incorrectly gave access to `apps.*`. Resource affected include: 

**Downstream clusters:**
apiservices
clusters
clusterrepos
persistentvolumes
storageclasses

**Rancher management cluster**
apprevisions
apps
catalogtemplates
catalogtemplateversions
clusteralertgroups
clusteralertrules
clustercatalogs
clusterloggings
clustermonitorgraphs
clusterregistrationtokens
clusterroletemplatebindings
clusterscans
etcdbackups
nodepools
nodes
notifiers
pipelineexecutions
pipelines
pipelinesettings
podsecuritypolicytemplateprojectbindings
projectalertgroups
projectalertrules
projectcatalogs
projectloggings
projectmonitorgraphs
projectroletemplatebindings
projects
secrets
sourcecodeproviderconfigs

There is not a direct mitigation besides upgrading to the patched Rancher versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25318
- https://github.com/rancher/rancher/issues/33590
- https://bugzilla.suse.com/show_bug.cgi?id=1184913
- https://github.com/rancher/rancher
- https://pkg.go.dev/vuln/GO-2024-2768
