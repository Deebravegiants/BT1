# [?] docs: clarify crediting process in vulnerability report (#9009)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2025-12-10
Source: https://github.com/starkware-libs/cairo/commit/05ed0b82a4f433dba9fd983a551c415bd7ea8dc0
Type: security-commit

## Details
docs: clarify crediting process in vulnerability report (#9009)

## Patch
### docs/SECURITY.md
```diff
@@ -9,7 +9,7 @@ If there are any vulnerabilities in **Cairo**, don't hesitate to _report them_.
 
    If you have a fix, that is most welcome -- please attach or summarize it in your message!
 
-3. We will evaluate the vulnerability and, if necessary, release a fix or mitigating steps to address it. We will contact you to let you know the outcome, and will credit you in the report.
+3. We will evaluate the vulnerability and, if necessary, release a fix or mitigation steps. We will contact you to let you know the outcome and credit you in the report.
 
    Please **do not disclose the vulnerability publicly** until a fix has been released!
 
```
