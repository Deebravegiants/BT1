# [C] Valtimo scripting engine can be used to gain access to sensitive data or resources

## Summary
Severity: Critical
Advisory: GHSA-w48j-pp7j-fj55
CVE: CVE-2025-58059
CWE: CWE-200, CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-w48j-pp7j-fj55
Type: github-advisory

## Affected
- Maven: `com.ritense.valtimo:core` — affected >=0 <12.16.0.RELEASE
- Maven: `com.ritense.valtimo:core` — affected >=13.0.0.RELEASE <13.1.2.RELEASE

## Details
### Impact
Any admin that can create or modify and execute process-definitions could gain access to sensitive data or resources.

This includes but is not limited to:
- Running executables on the application host
- Inspecting and extracting data from the host environment or application properties
- Spring beans (application context, database pooling)

### Attack requirements
The following conditions have to be met in order to perform this attack:
- The user must be logged in
- The user must have the admin role (ROLE_ADMIN), which is required to change process definitions
- The user must have some knowledge about running scripts via a the Camunda/Operator engine

### Patches
Version 12.16.0 and 13.1.2 have been patched. It is strongly advised to upgrade.

### Workarounds
If no scripting is needed in any of the processes, it could be possible to disable it altogether via the `ProcessEngineConfiguration`:
```
@Component
class NoScriptEnginePlugin : ProcessEnginePlugin {
    override fun preInit(processEngineConfiguration: ProcessEngineConfigurationImpl) {}

    override fun postInit(processEngineConfiguration: ProcessEngineConfigurationImpl) {
        processEngineConfiguration.scriptEngineResolver = null
    }

    override fun postProcessEngineBuild(processEngine: ProcessEngine) {}
}
```
Warning: this workaround could lead to unexpected side-effects. Please test thoroughly.

### References
- Valtimo 12 and lower: [Camunda Scripting](https://docs.camunda.org/manual/latest/user-guide/process-engine/scripting/#custom-scriptengineresolver)
- Valtimo 13 and higher: [Operaton Scripting](https://docs.operaton.org/docs/documentation/user-guide/process-engine/scripting)

## References
- https://github.com/valtimo-platform/valtimo-backend-libraries/security/advisories/GHSA-w48j-pp7j-fj55
- https://nvd.nist.gov/vuln/detail/CVE-2025-58059
- https://github.com/valtimo-platform/valtimo-backend-libraries/commit/45eb60b0b2df5964fb9917295d0dceb1fff8dd85
- https://github.com/valtimo-platform/valtimo-backend-libraries
