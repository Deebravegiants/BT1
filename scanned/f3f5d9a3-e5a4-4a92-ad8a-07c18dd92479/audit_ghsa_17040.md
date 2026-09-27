# [H] Insecure Variable Substitution in Vela

## Summary
Severity: High
Advisory: GHSA-pwx5-6wxg-px5h
CVE: CVE-2024-28236
CWE: CWE-200, CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-14
Source: https://github.com/advisories/GHSA-pwx5-6wxg-px5h
Type: github-advisory

## Affected
- Go: `github.com/go-vela/worker` — affected >=0 <0.23.2

## Details
### Impact
Vela pipelines can use variable substitution combined with insensitive fields like `parameters`, `image` and `entrypoint` to inject secrets into a plugin/image and — by using common substitution string manipulation — can bypass log masking and expose secrets without the use of the commands block. This unexpected behavior primarily impacts secrets restricted by the "no commands" option. This can lead to unintended use of the secret value, and increased risk of exposing the secret during image execution bypassing log masking.

Given by the following substitution examples:
using `parameters`
```yaml
steps:
  - name: example
    image: <some plugin>
    secrets: [ example_secret ]
    parameters:
      example: $${EXAMPLE_SECRET}
```

using `image` tag
```yaml
steps:
  - name: example
    image: <some plugin>:latest${EXAMPLE_SECRET}
    secrets: [ example_secret ]
```

using `entrypoint` as a shim for `commands`
```yaml
steps:
  - name: example
    image: <some plugin>
    secrets: [ example_secret ]
    entrypoint:
      [
        "sh",
        "-c",
        "echo $EXAMPLE_SECRET",
      ]
```



**To exploit this** the pipeline author must be supplying the secrets to a plugin that is designed in such a way that will print those parameters in logs. Plugin parameters are not designed for sensitive values and are often intentionally printed throughout execution for informational/debugging purposes. Parameters should therefore be treated as insensitive.

While Vela provides secrets masking, secrets exposure is not entirely solved by the masking process. A docker image (plugin) can easily expose secrets if they are not handled properly, or altered in some way. There is a responsibility on the end-user to understand how values injected into a plugin are used. This is a risk that exists for many CICD systems (like GitHub Actions) that handle sensitive runtime variables. Rather, the greater risk is that users who restrict a secret to the "no commands" option and use image restriction can still have their secret value exposed via substitution tinkering, which turns the image and command restrictions into a false sense of security.

### Patches
N/A

### Workarounds
- Do not provide sensitive values to plugins that can potentially expose them, especially in `parameters` that are not intended to be used for sensitive values.
- Ensure plugins (especially those that utilize shared secrets) follow best practices to avoid logging parameters that are expected to be sensitive.
- Minimize secrets with `pull_request` events enabled, as this allows users to change pipeline configurations and pull in secrets to steps not typically part of the CI process.
- Make use of the build approval setting, restricting builds from untrusted users
- Limit use of shared secrets, as they are less restrictive to access by nature.

### References
- https://github.com/go-vela/worker

### For more information

If you have any questions or comments about this advisory:

- Email us at [vela@target.com](mailto:vela@target.com)

Affected products: `go-vela/worker`

## References
- https://github.com/go-vela/worker/security/advisories/GHSA-pwx5-6wxg-px5h
- https://nvd.nist.gov/vuln/detail/CVE-2024-28236
- https://github.com/go-vela/worker/commit/e1572743b008e4fbce31ebb1dcd23bf6a1a30297
- https://github.com/go-vela/worker
