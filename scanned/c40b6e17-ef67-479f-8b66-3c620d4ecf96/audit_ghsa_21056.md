# [H] Argo CD improper access control bug can allow malicious user to escalate privileges to admin level

## Summary
Severity: High
Advisory: GHSA-96jv-vj39-x4j6
CVE: CVE-2022-1025
CWE: CWE-1220, CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-13
Source: https://github.com/advisories/GHSA-96jv-vj39-x4j6
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=0.5.0
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.1.14
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.2.0 <2.2.8
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.3.0 <2.3.2

## Details
# Impact

## Impacts for versions starting with v1.0.0
All unpatched versions of Argo CD starting with v1.0.0 are vulnerable to an improper access control bug, allowing a malicious user to potentially escalate their privileges to admin-level.

To perform the following exploits, an authorized Argo CD user must have push access to an Application's source git or Helm repository or `sync` and `override` access to an Application. Once a user has that access, different exploitation levels are possible depending on their other RBAC privileges:

1. If that user has `update` access to the Application, they can modify any resource on the Application's destination cluster. If the destination cluster is or can be made to be the same as the cluster hosting Argo CD, the user can escalate their Argo CD permissions to admin-level.
2. If the user has `delete` access to the Application, they can delete any resource on the Application's destination cluster. (This exploit is possible starting with v0.8.0.)
3. If the user has `get` access to the Application, they can view any resource on the Application's destination cluster (except for the contents of Secrets) and list [actions](https://argo-cd.readthedocs.io/en/stable/operator-manual/resource_actions/) available for that resource.
4. If the user has `get` access to the Application, they can view the logs of any Pods on the Application's destination cluster.
5. If the user has `action/{some action or *}` access on the Application, they can run an action for any resource (which supports the allowed action(s)) on the Application's destination cluster. (Some actions are available in Argo CD by default, and others may be configured by an Argo CD admin.)

See the [Argo CD RBAC documentation](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/#rbac-resources-and-actions) for an explanation of the privileges available in Argo CD.

## Events exploit
A related exploit is possible for a user with `get` access to an Application **even if they do not have access to the Application's source git or Helm repository or `sync` and `override` access to the Application**. The user can access any Event in the Application's destination cluster if they know the involved object's name, UID, and namespace.

## Impacts for versions starting with v0.8.0
The same bug exists starting with v0.8.0, but only the following exploits were possible before v1.0.0:

- The `delete exploit` (#⁠2 above).
- The logs exploit (#⁠4 above).
- The Events exploit described above.

## Impacts for versions starting with v0.5.0
The same bug exists starting with v0.5.0 (when RBAC was implemented), but only the Events exploit described above was possible before v0.8.0.

Patches
A patch for this vulnerability has been released in the following Argo CD versions:

- v2.3.2
- v2.2.8
- v2.1.14

**Versions 2.0.x and earlier users**: See the changelog for links to upgrade instructions for your version. It is imperative to upgrade quickly, but some limited mitigations are described in the next section.

**argo-helm chart users**: Argo CD users deploying v2.3.x with argo-helm can upgrade the chart to version 4.2.2. Argo CD 2.2 and 2.1 users can set the global.image.tag value to the latest in your current release series (v2.2.8, or v2.1.14). Since charts for the 2.2 and 2.1 series are no longer maintained, you will need to either leave the value override in place or upgrade to the 4.x chart series (and therefore to Argo CD 2.3).

## Workarounds
The only certain way to avoid the vulnerability is to upgrade.

## Mitigations

- To avoid privilege escalation:
    - Limit who has push access to Application source repositories or sync + override access to Applications.
- Limit which repositories are available in projects where users have update access to Applications.
    - To avoid unauthorized resource inspection/tampering:
    - Limit who has delete, get, or action access to Applications.

These mitigations can help limit potential damage, but they are not a substitute for upgrading. It is necessary to upgrade immediately.

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-2f5v-8r3f-8pww
- https://nvd.nist.gov/vuln/detail/CVE-2022-1025
- https://github.com/argoproj/argo-cd/commit/af03b291d4b7e9d3ce9a6580ae9c8141af0e05cf
- https://access.redhat.com/errata/RHSA-2022:1039
- https://access.redhat.com/errata/RHSA-2022:1040
- https://access.redhat.com/errata/RHSA-2022:1041
- https://access.redhat.com/errata/RHSA-2022:1042
- https://access.redhat.com/security/cve/CVE-2022-1025
- https://bugzilla.redhat.com/show_bug.cgi?id=2064682
- https://github.com/argoproj/argo-cd
