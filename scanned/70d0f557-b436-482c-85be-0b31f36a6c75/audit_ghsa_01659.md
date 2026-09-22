# [H] Remote Code Execution (RCE) vulnerability in dropwizard-validation

## Summary
Severity: High
Advisory: GHSA-3mcp-9wr4-cjqf
CVE: CVE-2020-5245
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2020-02-24
Source: https://github.com/advisories/GHSA-3mcp-9wr4-cjqf
Type: github-advisory

## Affected
- Maven: `io.dropwizard:dropwizard-validation` — affected >=1.3.0-rc1 <1.3.19
- Maven: `io.dropwizard:dropwizard-validation` — affected >=2.0.0 <2.0.2

## Details
Dropwizard-Validation before 1.3.19, and 2.0.2 may allow arbitrary code execution on the host system, with the privileges of the Dropwizard service account, by injecting arbitrary Java Expression Language expressions when using the self-validating feature.

### Summary

A server-side template injection was identified in the self-validating ([`@SelfValidating`](https://javadoc.io/static/io.dropwizard/dropwizard-project/2.0.2/io/dropwizard/validation/selfvalidating/SelfValidating.html)) feature of **dropwizard-validation** enabling attackers to inject arbitrary Java EL expressions, leading to Remote Code Execution (RCE) vulnerability.

If you're using a self-validating bean (via [`@SelfValidating`](https://javadoc.io/static/io.dropwizard/dropwizard-project/2.0.2/io/dropwizard/validation/selfvalidating/SelfValidating.html)), an upgrade to Dropwizard 1.3.19 or 2.0.2 is strongly recommended.

### Impact

This issue may allow Remote Code Execution (RCE), allowing to run arbitrary code on the host system (with the privileges of the Dropwizard service account privileges) by injecting arbitrary [Java Expression Language (EL)](https://docs.jboss.org/hibernate/validator/6.1/reference/en-US/html_single/#section-interpolation-with-message-expressions) expressions when using the self-validating feature ([`@SelfValidating`](https://javadoc.io/static/io.dropwizard/dropwizard-project/2.0.2/io/dropwizard/validation/selfvalidating/SelfValidating.html), [`@SelfValidation`](https://javadoc.io/static/io.dropwizard/dropwizard-project/2.0.2/io/dropwizard/validation/selfvalidating/SelfValidation.html)) in **dropwizard-validation**.

### Patches

The issue has been fixed in **dropwizard-validation** **1.3.19** and **2.0.2**. We strongly recommend upgrading to one of these versions.

### Workarounds

If you are not able to upgrade to one of the aforementioned versions of **dropwizard-validation** but still want to use the [`@SelfValidating`](https://javadoc.io/static/io.dropwizard/dropwizard-project/2.0.2/io/dropwizard/validation/selfvalidating/SelfValidating.html) feature, make sure to properly sanitize any message you're adding to the [`ViolationCollector`](https://javadoc.io/static/io.dropwizard/dropwizard-project/2.0.2/io/dropwizard/validation/selfvalidating/ViolationCollector.html) in the method annotated with [`@SelfValidation`](https://javadoc.io/static/io.dropwizard/dropwizard-project/2.0.2/io/dropwizard/validation/selfvalidating/SelfValidation.html).

Example:
```java
@SelfValidation
public void validateFullName(ViolationCollector col) {
    if (fullName.contains("_")) {
        // Sanitize fullName variable by escaping relevant characters such as "$"
        col.addViolation("Full name contains invalid characters:  " + sanitizeJavaEl(fullName));
    }
}
```

See also:
https://github.com/dropwizard/dropwizard/blob/v2.0.2/dropwizard-validation/src/main/java/io/dropwizard/validation/selfvalidating/ViolationCollector.java#L84-L98

### References

* https://github.com/dropwizard/dropwizard/pull/3157
* https://github.com/dropwizard/dropwizard/pull/3160
* https://docs.oracle.com/javaee/7/tutorial/jsf-el.htm
* https://docs.jboss.org/hibernate/validator/6.1/reference/en-US/html_single/#section-interpolation-with-message-expressions
* https://beanvalidation.org/2.0/spec/#validationapi-message-defaultmessageinterpolation

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [dropwizard/dropwizard](https://github.com/dropwizard/dropwizard/issues/new)
* Start a discussion on the [dropwizard-dev mailing list](https://groups.google.com/forum/#!forum/dropwizard-dev)

### Security contact

If you want to responsibly disclose a security issue in Dropwizard or one of its official modules, please contact us via the published channels in our [security policy](https://github.com/dropwizard/dropwizard/security/policy):

https://github.com/dropwizard/dropwizard/security/policy#reporting-a-vulnerability

## References
- https://github.com/dropwizard/dropwizard/security/advisories/GHSA-3mcp-9wr4-cjqf
- https://nvd.nist.gov/vuln/detail/CVE-2020-5245
- https://github.com/dropwizard/dropwizard/pull/3157
- https://github.com/dropwizard/dropwizard/pull/3160
- https://github.com/dropwizard/dropwizard/commit/28479f743a9d0aab6d0e963fc07f3dd98e8c8236
- https://github.com/dropwizard/dropwizard/commit/d87d1e4f8e20f6494c0232bf8560c961b46db634
- https://beanvalidation.org/2.0/spec/#validationapi-message-defaultmessageinterpolation
- https://docs.jboss.org/hibernate/validator/6.1/reference/en-US/html_single/#section-interpolation-with-message-expressions
- https://docs.oracle.com/javaee/7/tutorial/jsf-el.htm
- https://github.com/dropwizard/dropwizard
- https://www.oracle.com/security-alerts/cpuapr2022.html
