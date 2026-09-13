# [C] Apache NiFi: Missing Authorization for Components Referenced by Parameter Context Updates

## Summary
Severity: Critical
Advisory: BIT-nifi-2026-68979
Aliases: CVE-2026-68979
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-nifi-2026-68979
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.10.0 <2.11.0

## Details
Apache NiFI 1.10.0 through 2.10.0 provide a Parameter Context update REST API method that does not enforce authorization checking on components referencing Parameter values. Updating a Parameter Context can change parameter values that affect referencing components, but framework authorization was limited to read and write privileges on the Parameter Context itself. As a result of the missing authorization, an authenticated user authorized to modify a Parameter Context, but not authorized on referencing components, could alter Parameter values affecting those components. In deployments where a Parameter value contains executable scripting content, updating a Parameter can result in code execution during automatic component validation, without starting the referencing component. The impact was limited to stopped components by existing verification checks, and the issue applies only to deployments that use component-level authorization policies. Upgrading to Apache NiFi 2.11.0 is the recommended mitigation, which aligns the Parameter Context update method authorization with other methods, adding authorization checking on affected components.

## References
- http://www.openwall.com/lists/oss-security/2026/08/03/10
- https://lists.apache.org/thread/xwz8wsss2ovx07tns96rkc3n7cm4xfrq
- https://nvd.nist.gov/vuln/detail/CVE-2026-68979
