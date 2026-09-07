# [M]  GeoServer's Server Status shows sensitive environmental variables and Java properties

## Summary
Severity: Medium
Advisory: GHSA-j59v-vgcr-hxvf
CVE: CVE-2024-34696
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-j59v-vgcr-hxvf
Type: github-advisory

## Affected
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.10.0 <2.24.4
- Maven: `org.geoserver.web:gs-web-app` — affected >=2.25.0 <2.25.1
- Maven: `org.geoserver:gs-main` — affected >=2.10.0 <2.24.4
- Maven: `org.geoserver:gs-main` — affected >=2.25.0 <2.25.1

## Details
GeoServer's Server Status page and REST API (at `/geoserver/rest/about/status`) lists *all* environment variables and Java properties to *any* GeoServer user with administrative rights as part of those modules' status message.

These variables/properties can also contain sensitive information, such as database passwords or API keys/tokens, for example:

* Data stores defined with [parameterized catalog settings][catalog] (`-DALLOW_ENV_PARAMETRIZATION=true`) which need a password or access key.

* GeoServer's official Docker image [uses environment variables to configure PostgreSQL JNDI resources, including credentials][docker-jndi] (`POSTGRES_HOST`, `POSTGRES_USERNAME`, `POSTGRES_PASSWORD`)

Additionally, many community-developed GeoServer container images `export` other credentials from their start-up scripts as environment variables to the GeoServer (`java`) process, such as:

* GeoServer `admin` and master (`root`) passwords

* Tomcat management application password

* HTTPS/TLS certificate key store password

* AWS S3 bucket access keys

The precise scope of the issue depends on which container image is used and how it is configured.

> [!NOTE]
> Some container images allow passing secrets as files (eg: `POSTGRES_PASSWORD_FILE`), or randomly generating passwords on start-up. While this is promoted as best-practice[^secret-files], if its start-up script [`export`s these as environment variables][bash-export] to GeoServer, they are **also** impacted by this issue.

[bash-export]: https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html#index-export
[catalog]: https://docs.geoserver.org/latest/en/user/datadirectory/configtemplate.html
[docker-jndi]: https://github.com/geoserver/docker/blob/master/README.md#how-to-enable-a-postgresql-jndi-resource

### Impact

The “about status” API endpoint (at `/geoserver/rest/about/status`) which powers the Server Status page is only available to administrators.

Depending on the operating environment, administrators might have legitimate access to credentials in other ways, but this issue defeats more sophisticated controls (like break-glass access to secrets or role accounts).

By default, GeoServer only allows same-origin authenticated API access. This limits the scope for a third-party attacker to use an administrator’s credentials to gain access to credentials (ie: requires XSS).

We were unable to determine any other conditions under which the GeoServer REST API may be available more broadly.

### Fixes / remediation

GeoServer 2.24.4 and 2.25.1 hide **all** environment variables and Java system properties *by default*, with *no further action required by GeoServer administrators*.

[There are new settings to allow an administrator to display these again][showing] – effectively **reverting** this security fix. We strongly recommend administrators leave these settings as-is, and use alternative mechanisms to access environment variables (instructions below).

If you're using GeoServer in a container runtime (such as Docker or Kubernetes) or from some other distributor's packages, you'll need to wait for the maintainer to update the version of GeoServer used in their image.

> [!WARNING]
> If you run GeoServer with [parameterized catalog settings][catalog] (`-DALLOW_ENV_PARAMETRIZATION=true`), a GeoServer administrator could use this to access any environment variable or Java property by including it in some field which is rendered by the UI (such as the description field), **even with this fix**.

[showing]: https://docs.geoserver.org/latest/en/user/production/config.html#showing-environment-variables-and-java-system-properties

### Advice for container / Docker image maintainers

Update container images to use GeoServer 2.24.4 or 2.25.1 to get the bug fix.

Please leave environment variables and Java system properties hidden by default. If you provide the option to re-enable it, [communicate the impact and risks][showing] so that users can make an informed choice.

Container images should practice "defence in depth", to limit the impact when it is configured to show environment variables and/or properties:

* Pass secrets to the container as either:

  * files which are only readable by the GeoServer process/UID, or,
  * references (identifiers) to a secret stored in a cloud provider's metadata or secret management service

* Pass secrets to GeoServer by generating configuration files as part of your start-up scripts, rather than passing variables/properties or relying on [parameterized catalog settings][catalog].

* Ensure any configuration files with secrets are not readable by other users.

* Clear all environment variables which contain secrets _before_ starting GeoServer.

  _Alternatively:_ start up GeoServer with *only* the environment variables it needs, and no secrets.

* **Don't** pass secrets as command-line flags – these are shown in `ps` to all users!

### Alternatives for displaying GeoServer's environment variables

* **On Linux,** you can get all environment variables [set at _start-up time_][linux-environ] for a running process with:

  ```sh
  tr '\0' '\n' < /proc/${GEOSERVER_PID}/environ
  ```

* **On Windows,** [SysInternals' Process Explorer][proc-exp] can show running processes' environment variables.

* Current versions of **macOS** do not allow arbitrary access to other running processes' environment variables. Disabling these restrictions (on a macOS level) would significantly reduce the overall security of the system.

[linux-environ]: https://unix.stackexchange.com/a/70636
[proc-exp]: https://learn.microsoft.com/en-us/sysinternals/downloads/process-explorer

[^secret-files]: [Docker Compose: How to use secrets in Docker Compose](https://docs.docker.com/compose/use-secrets/), [Docker Swarm: Build support for Docker Secrets into your images](https://docs.docker.com/engine/swarm/secrets/#build-support-for-docker-secrets-into-your-images)

## References
- https://github.com/geoserver/geoserver/security/advisories/GHSA-j59v-vgcr-hxvf
- https://nvd.nist.gov/vuln/detail/CVE-2024-34696
- https://github.com/geoserver/geoserver
