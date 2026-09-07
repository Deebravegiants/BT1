# [M] Helm passes repository credentials to alternate domain

## Summary
Severity: Medium
Advisory: GHSA-56hp-xqp3-w2jf
CVE: CVE-2021-32690
CWE: CWE-200
Ecosystem: Go
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-56hp-xqp3-w2jf
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.6.1

## Details
While working on the Helm source, a Helm core maintainer discovered a situation where the username and password credentials associated with a Helm repository could be passed on to another domain referenced by that Helm repository.

### Impact

The `index.yaml` within a Helm chart repository contains a reference where to get the chart archive for each version of a chart. The reference can be relative to the `index.yaml` file or a URL to location. The URL can point to any domain and this is a feature leveraged by Helm users. For example, an `index.yaml` file can be hosted on GitHub pages while the chart archives are hosted as GitHub releases. These are on different domain names and the `index.yaml` file points to the other domain.

When a username and password were associated with a Helm repository the username and password were also passed on to other domains referenced in the `index.yaml` file. This occurred when Helm went to retrieve a specific chart archive on the other domain.

### Patches

This issue has been resolved in 3.6.1.

There is a slight behavior change to credential handling with regard to repositories. Usernames and passwords are only passed to the URL location of the Helm repository by default. The username and password are scoped to the scheme, host, and port of the Helm repository. To pass the username and password to other domains Helm may encounter when it goes to retrieve a chart, the new `--pass-credentials` flag can be used. This flag restores the old behavior for a single repository as an opt-in behavior.

### Workarounds

If you use a username and password for a Helm repository you can audit the Helm repository in order to check for another domain being used that could have received the credentials. In the `index.yaml` file for that repository, look for another domain in the `urls` list for the chart versions. If there is another domain found and that chart version was pulled or installed the credentials would have been passed on.

### For more information

Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

## References
- https://github.com/helm/helm/security/advisories/GHSA-56hp-xqp3-w2jf
- https://nvd.nist.gov/vuln/detail/CVE-2021-32690
- https://github.com/helm/helm/commit/61d8e8c4a6f95540c15c6a65f36a6dd0a45e7a2f
- https://github.com/helm/helm
- https://github.com/helm/helm/releases/tag/v3.6.1
- https://pkg.go.dev/vuln/GO-2022-0384
