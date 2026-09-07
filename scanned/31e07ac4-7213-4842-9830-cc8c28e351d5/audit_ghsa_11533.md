# [C] OneUptime: Synthetic Monitor RCE via exposed Playwright browser object

## Summary
Severity: Critical
Advisory: GHSA-4j36-39gm-8vq8
CVE: CVE-2026-30921
CWE: CWE-749
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-4j36-39gm-8vq8
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <10.0.20

## Details
Summary

OneUptime Synthetic Monitors allow low-privileged project users to submit custom Playwright code that is executed on the `oneuptime-probe` service. In the current implementation, this untrusted code is run inside Node's `vm` and is given live host Playwright objects such as `browser` and `page`.

This creates a distinct server-side RCE primitive: the attacker does not need the classic `this.constructor.constructor(...)` sandbox escape. Instead, the attacker can directly use the injected Playwright `browser` object to reach `browser.browserType().launch(...)` and spawn an arbitrary executable on the probe host/container.

This appears to be a separate issue from the previously published `node:vm(GHSA-h343-gg57-2q67)` breakout advisory because the root cause here is exposure of a dangerous host capability object to untrusted code, not prototype-chain access to `process`.

## Details

A normal project member can create or edit monitors and monitor tests:

- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Common/Models/DatabaseModels/Monitor.ts#L45-L78
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Common/Models/DatabaseModels/MonitorTest.ts#L27-L60

The dashboard exposes a Playwright code editor for Synthetic Monitors and allows the user to queue a test run:

- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/App/FeatureSet/Dashboard/src/Components/Form/Monitor/MonitorStep.tsx#L861-L918
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/App/FeatureSet/Dashboard/src/Components/Form/Monitor/MonitorTest.tsx#L66-L84

The probe worker polls queued monitor tests and executes them:

- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Jobs/Monitor/FetchMonitorTest.ts#L55-L85

For `MonitorType.SyntheticMonitor`, the user-controlled `customCode` is passed into `SyntheticMonitor.execute(...)`:

- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Utils/Monitors/Monitor.ts#L323-L338

`SyntheticMonitor.execute(...)` then runs that code through `VMRunner.runCodeInNodeVM(...)` and injects the live Playwright `browser` and `page` objects into the VM context:

- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Utils/Monitors/MonitorTypes/SyntheticMonitor.ts#L156-L168

`VMRunner.runCodeInNodeVM(...)` creates a Node `vm` context and exposes host objects into it, including the additional context objects:

- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Common/Server/Utils/VM/VMRunner.ts#L323-L405

The proxy wrapper blocks only a small set of property names and still forwards normal method calls with the real host `this` binding. Because of that, untrusted monitor code can still use legitimate Playwright methods on the injected `browser` object.

That is enough for code execution because Playwright's `Browser` exposes `browserType()`, and `BrowserType.launch()` accepts attacker-controlled process launch options such as `executablePath`, `args`, and `ignoreDefaultArgs`. An attacker can therefore cause the probe to spawn an arbitrary executable. Even if Playwright later errors because the spawned process is not a real browser, the command has already executed.

This same execution path is also used for normal scheduled monitors, not only one-shot monitor tests:

- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Jobs/Monitor/FetchList.ts#L110-L121

As a result, the issue can be abused either as a one-shot RCE via `Test Monitor` or as a persistent scheduled RCE by saving a malicious Synthetic Monitor.

### PoC

1. Log in as any user with normal project membership.
2. Go to `Monitors -> Create New Monitor`.
3. Select `Synthetic Monitor`.
4. In `Playwright Code`, paste the following script:

```javascript
 const HostFunction =
    Object.getOwnPropertyDescriptor(console, "log").value.constructor;

  return {
    data: {
      node: HostFunction('return process.version')(),
      cwd: HostFunction('return process.cwd()')(),
      id: HostFunction(
        'return process.getBuiltinModule("child_process").execSync("id").toString()'
      )(),
    },
  };

```

5. Select any one browser type, for example `Chromium`.
6. Select any one screen type, for example `Desktop`.
7. Set retry count to `0`.
8. Click `Test Monitor` and choose a probe.

Expected result:

- the monitor execution succeeded and in the `Show More Details` the command output is shown.
<img width="899" height="249" alt="image" src="https://github.com/user-attachments/assets/98ebd26f-431b-438e-9459-7deeebf97b18" />



### Impact

This is a server-side `Remote Code Execution` issue affecting the probe component.

Who is impacted:

- any OneUptime deployment where an attacker can obtain ordinary project membership
- environments where the probe has access to internal services, secrets, Kubernetes metadata, database credentials, proxy credentials, or other cluster-local trust relationships

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-4j36-39gm-8vq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-30921
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/App/FeatureSet/Dashboard/src/Components/Form/Monitor/MonitorStep.tsx#L861-L918
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/App/FeatureSet/Dashboard/src/Components/Form/Monitor/MonitorTest.tsx#L66-L84
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Common/Models/DatabaseModels/Monitor.ts#L45-L78
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Common/Models/DatabaseModels/MonitorTest.ts#L27-L60
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Common/Server/Utils/VM/VMRunner.ts#L323-L405
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Jobs/Monitor/FetchList.ts#L110-L121
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Jobs/Monitor/FetchMonitorTest.ts#L55-L85
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Utils/Monitors/Monitor.ts#L323-L338
- https://github.com/OneUptime/oneuptime/blob/8e90f451426b160718bdd1796b68c5ec15318101/Probe/Utils/Monitors/MonitorTypes/SyntheticMonitor.ts#L156-L168
