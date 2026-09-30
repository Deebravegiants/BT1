# [C] OpenIdentityPlatform OpenAM: Pre-Authentication Remote Code Execution via `jato.clientSession` Deserialization in OpenAM

## Summary
Severity: Critical
Advisory: GHSA-2cqq-rpvq-g5qj
CVE: CVE-2026-33439
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-2cqq-rpvq-g5qj
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam` — affected >=0 <16.0.6

## Details
## Summary

OpenIdentityPlatform OpenAM 16.0.5 (and likely earlier versions) is vulnerable to pre-authentication Remote Code Execution (RCE) via unsafe Java deserialization of the `jato.clientSession` HTTP parameter. This bypasses the `WhitelistObjectInputStream` mitigation that was applied to the `jato.pageSession` parameter after CVE-2021-35464.

An unauthenticated attacker can achieve arbitrary command execution on the server by sending a crafted serialized Java object as the `jato.clientSession` GET/POST parameter to any JATO ViewBean endpoint whose JSP contains `<jato:form>` tags (e.g., the Password Reset pages).

---

## Vulnerability Details

### Background

CVE-2021-35464 identified that the `jato.pageSession` HTTP parameter was deserialized without class filtering, allowing pre-auth RCE.

OpenIdentityPlatform OpenAM mitigated this by introducing `WhitelistObjectInputStream` in `ConsoleViewBeanBase.deserializePageAttributes()`, which restricts `jato.pageSession` deserialization to a hardcoded whitelist of ~40 safe classes.

However, the JATO framework contains a **second deserialization entry point** — `jato.clientSession` — handled by `ClientSession.deserializeAttributes()`. This code path was **not patched** and still uses the unfiltered `Encoder.deserialize()` → `ApplicationObjectInputStream`, which performs `ObjectInputStream.readObject()` with no class whitelist.

### Root Cause

```
ClientSession.deserializeAttributes()
  → Encoder.deserialize()
    → ApplicationObjectInputStream.readObject()  // VULNERABLE — no whitelist
```

The `ClientSession` object is instantiated in `RequestContextImpl.getClientSession()` with the raw `jato.clientSession` parameter value from the HTTP request. Deserialization is triggered during JSP rendering when `<jato:form>` tags invoke `getClientSession()` → `hasAttributes()` → `getEncodedString()` → `isValid()` → `ensureAttributes()` → `deserializeAttributes()`.

### Affected Code

**File:** `com/iplanet/jato/ClientSession.java`
```java
protected ClientSession(RequestContext context) {
    this.encodedSessionString =
        context.getRequest().getParameter("jato.clientSession");
}

protected void deserializeAttributes() {
    if (this.encodedSessionString != null
        && this.encodedSessionString.trim().length() > 0) {
        this.setAttributes(
            (Map) Encoder.deserialize(
                Encoder.decodeHttp64(this.encodedSessionString), false)
        );
    }
}
```

### Gadget Chain

The exploit uses classes bundled in the OpenAM WAR:

```
PriorityQueue.readObject()                        [java.util — JDK]
  → heapify() → siftDown() → comparator.compare()
    → Column$ColumnComparator.compare()            [openam-core-16.0.5.jar]
      → Column.getProperty()
        → PropertyUtils.getObjectPropertyValue()   [openam-core-16.0.5.jar]
          → Method.invoke(TemplatesImpl, "getOutputProperties")
            → TemplatesImpl.getOutputProperties()  [xalan-2.7.3.jar]
              → newTransformer() → defineTransletClasses()
                → TransletClassLoader.defineClass(_bytecodes)
                  → _class[_transletIndex].newInstance()
                    → EvilTranslet.<clinit>()      [attacker bytecode]
                      → Runtime.getRuntime().exec(cmd)
```

---

## Impact

- **Pre-authentication** — no credentials or session tokens required
- **Remote Code Execution** — arbitrary OS commands as the application server user
- Full server compromise, lateral movement, data exfiltration
- Affects any deployment with at least one accessible JATO endpoint whose JSP renders `<jato:form>` tags (e.g., Password Reset pages)

---

## Tested Environment

- OpenIdentityPlatform OpenAM 16.0.5 (official release WAR from GitHub)
- Apache Tomcat 10.1.52
- Java 21.0.7 (Oracle JDK)
- macOS / Linux (aarch64)
- Also verified on `openidentityplatform/openam:latest` Docker image (Java 25)

## Affected Versions

- OpenIdentityPlatform OpenAM 16.0.5 (confirmed on both Docker and bare-metal Tomcat)
- Likely all versions that left `ClientSession.deserializeAttributes()` unpatched

---

## Remediation

1. Apply `WhitelistObjectInputStream` filtering to `ClientSession.deserializeAttributes()`, matching the mitigation already applied to `ConsoleViewBeanBase.deserializePageAttributes()`
2. Audit all callers of `Encoder.deserialize()` for user-controlled input
3. Consider adding a JVM-wide JEP 290 deserialization filter as defense-in-depth

---

## References

- CVE-2021-35464 — Pre-auth RCE in ForgeRock OpenAM (PortSwigger Research)
- https://portswigger.net/research/pre-auth-rce-in-forgerock-openam-cve-2021-35464
- CWE-502: Deserialization of Untrusted Data

---

## Credit

This finding was discovered by **Rahul Maini and Hacktron AI** while auditing OpenIdentityPlatform OpenAM. Hacktron AI is our white-box pentest solution, designed to deliver high-accuracy results with minimal false positives.

---

## Disclosure Policy

This bug is subject to a 90-day disclosure deadline. If a fix for this issue is made available to users before the end of the 90-day deadline, this bug report will become public on the day that the fix was made available or an earlier or later date if agreed by both parties. Otherwise, this bug report will become public at the deadline.

If another researcher discloses the proof-of-concept before any deadlines, we reserve the right to publish our findings.

The details of this bug may be privately disclosed to vulnerable parties, including but not limited to Hacktron AI's customers.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-2cqq-rpvq-g5qj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33439
- https://github.com/OpenIdentityPlatform/OpenAM/commit/014007c63cacc834cc795a89fac0e611aebc4a32
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.0.6
