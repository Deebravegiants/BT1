# [M] CommandKit has incorrect command name exposure in context object for message command aliases

## Summary
Severity: Medium
Advisory: GHSA-fhwm-pc6r-4h2f
CVE: CVE-2025-62378
CWE: CWE-706
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-fhwm-pc6r-4h2f
Type: github-advisory

## Affected
- npm: `commandkit` — affected >=1.2.0-rc.1 <1.2.0-rc.12

## Details
### Impact

A logic flaw exists in the message command handler of CommandKit that affects how the `commandName` property is exposed to both middleware functions and command execution contexts when handling command aliases. When a message command is invoked using an alias, the `ctx.commandName` value reflects the alias rather than the canonical command name. This occurs in both middleware functions and within the command’s own run function.

Although not explicitly documented, CommandKit’s examples and guidance around middleware usage implicitly convey that `ctx.commandName` represents the canonical command identifier. Middleware examples in the documentation consistently use `ctx.commandName` to reference the command being executed, and the documentation describes middleware as suitable for “logging, authentication, permission checks, or any other cross-cutting concerns.” As a result, developers reasonably expect `ctx.commandName` to return the canonical command name and may rely on it for security-sensitive logic.

Developers who assume `ctx.commandName` is canonical may introduce unintended behavior when relying on it for logic such as permission checks, rate limiting, or audit logging. This could allow unauthorized command execution or inaccurate access control decisions. Slash commands and context menu commands are not affected.

### Patches

Fixed in v1.2.0-rc.12.
`ctx.commandName` now consistently returns the actual canonical command name, regardless of the alias used to invoke it.

### Workaround

If upgrading isn't immediately possible:

* Use `ctx.command.data.command.name` for permission validations, or
* Include all command aliases in your permission logic.

### References

* [CommandKit repository](https://github.com/underctrl-io/commandkit)
* [Middleware documentation](https://commandkit.dev/docs/guide/commands/middlewares)

## References
- https://github.com/underctrl-io/commandkit/security/advisories/GHSA-fhwm-pc6r-4h2f
- https://nvd.nist.gov/vuln/detail/CVE-2025-62378
- https://github.com/underctrl-io/commandkit/commit/440385a3e5de3fa3d2a76d23a807995cb29602fd
- https://github.com/underctrl-io/commandkit
