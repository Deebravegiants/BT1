# [M] Configuration API in EdgeXFoundry 2.1.0 and earlier exposes message bus credentials to local unauthenticated users

## Summary
Severity: Medium
Advisory: GHSA-g63h-q855-vp3q
CVE: CVE-2022-31066
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-g63h-q855-vp3q
Type: github-advisory

## Affected
- Go: `github.com/edgexfoundry/device-sdk-go/v2` — affected >=0 <2.1.1
- Go: `github.com/edgexfoundry/app-functions-sdk-go/v2` — affected >=0 <2.1.1

## Details
### Impact
The /api/v2/config endpoint exposes message bus credentials to local unauthenticated users.  In security-enabled mode, message bus credentials are supposed to be kept in the EdgeX secret store and require authentication to access.  This vulnerability bypasses the access controls on message bus credentials when running in security-enabled mode.  (No credentials are required when running in security-disabled mode.)  As a result, attackers could intercept data or inject fake data into the EdgeX message bus.

### Patches
Users should upgrade to EdgeXFoundry Kamakura release (2.2.0) or to the June 2022 EdgeXFoundry LTS Jakarta release (2.1.1).

The issue has been patched in the following docker containers and snaps:

#### Patched go modules
github.com/edgexfoundry/device-sdk-go/v2 >= v2.1.1
github.com/edgexfoundry/app-functions-sdk-go/v2 >= v2.1.1

#### Patched docker containers
URL: https://hub.docker.com/r/edgexfoundry
- docker.io/edgexfoundry/core-metadata:>=2.1.1
- docker.io/edgexfoundry/core-metadata-arm64:>=2.1.1
- docker.io/edgexfoundry/core-data:>=2.1.1
- docker.io/edgexfoundry/core-data-arm64:>=2.1.1
- docker.io/edgexfoundry/core-command:>=2.1.1
- docker.io/edgexfoundry/core-command-arm64:>=2.1.1
- docker.io/edgexfoundry/support-notifications:>=2.1.1
- docker.io/edgexfoundry/support-notifications-arm64:>=2.1.1
- docker.io/edgexfoundry/support-scheduler:>=2.1.1
- docker.io/edgexfoundry/support-scheduler-arm64:>=2.1.1
- docker.io/edgexfoundry/sys-mgmt-agent:>=2.1.1
- docker.io/edgexfoundry/sys-mgmt-agent-arm64:>=2.1.1
- docker.io/edgexfoundry/security-proxy-setup:>=2.1.1
- docker.io/edgexfoundry/security-proxy-setup-arm64:>=2.1.1
- docker.io/edgexfoundry/security-secretstore-setup:>=2.1.1
- docker.io/edgexfoundry/security-secretstore-setup-arm64:>=2.1.1
- docker.io/edgexfoundry/security-bootstrapper:>=2.1.1
- docker.io/edgexfoundry/security-bootstrapper-arm64:>=2.1.1
- docker.io/edgexfoundry/app-rfid-llrp-inventory:>=2.1.1
- docker.io/edgexfoundry/app-rfid-llrp-inventory-arm64:>=2.1.1
- docker.io/edgexfoundry/app-service-configurable:>=2.1.1
- docker.io/edgexfoundry/app-service-configurable-arm64:>=2.1.1
- docker.io/edgexfoundry/device-camera:>=2.2.0
- docker.io/edgexfoundry/device-camera-arm64:>=2.2.0
- docker.io/edgexfoundry/device-gpio:>=2.1.1
- docker.io/edgexfoundry/device-gpio-arm64:>=2.1.1
- docker.io/edgexfoundry/device-modbus:>=2.1.1
- docker.io/edgexfoundry/device-modbus-arm64:>=2.1.1
- docker.io/edgexfoundry/device-mqtt:>=2.1.1
- docker.io/edgexfoundry/device-mqtt-arm64:>=2.1.1
- docker.io/edgexfoundry/device-rest:>=2.1.1
- docker.io/edgexfoundry/device-rest-arm64:>=2.1.1
- docker.io/edgexfoundry/device-rfid-llrp:>=2.1.1
- docker.io/edgexfoundry/device-rfid-llrp-arm64:>=2.1.1
- docker.io/edgexfoundry/device-snmp:>=2.1.1
- docker.io/edgexfoundry/device-snmp-arm64:>=2.1.1
- docker.io/edgexfoundry/device-virtual:>=2.1.1
- docker.io/edgexfoundry/device-virtual-arm64:>=2.1.1

#### Patched snaps
URL: https://snapcraft.io/edgexfoundry
edgexfoundry  2.1/stable  (will be automatically upgraded to 2.1.1)

### Workarounds
No workaround available.

### References
* https://github.com/edgexfoundry/edgex-go/security/advisories/GHSA-g63h-q855-vp3q
* https://github.com/edgexfoundry/device-sdk-go/pull/1161 (patch against Kamakura)
* https://github.com/edgexfoundry/edgex-go/pull/4016 (patch against Kamakura)
* https://github.com/edgexfoundry/edgex-go/pull/4039 (cherry-pick patch against Jakarta)
* https://github.com/edgexfoundry/device-sdk-go/pull/1167 (differs from patch on main: don't copy PW in vs delete it after)

### For more information
If you have any questions or comments about this advisory:
* Contact us in the [Slack #security channel](https://slack.edgexfoundry.org/)
* Open an issue in [edgex-go](https://github.com/edgexfoundry/edgex-go)
* Email us at [EdgeX-TSC-Security@lists.edgexfoundry.org](mailto:EdgeX-TSC-Security@lists.edgexfoundry.org)

## References
- https://github.com/edgexfoundry/edgex-go/security/advisories/GHSA-g63h-q855-vp3q
- https://nvd.nist.gov/vuln/detail/CVE-2022-31066
- https://github.com/edgexfoundry/device-sdk-go/pull/1161
- https://github.com/edgexfoundry/edgex-go/pull/4016
- https://github.com/edgexfoundry/edgex-go
