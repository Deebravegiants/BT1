# [H] CSRF protection for any URL can be bypassed in Jenkins Pipeline: Input Step Plugin

## Summary
Severity: High
Advisory: GHSA-g66m-fqxf-3w35
CVE: CVE-2022-43407
CWE: CWE-352, CWE-838
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-g66m-fqxf-3w35
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-input-step` — affected >=0 <456.vd8a_957db_5b_e9

## Details
Pipeline: Input Step Plugin 451.vf1a_a_4f405289 and earlier does not restrict or sanitize the optionally specified ID of the `input` step. This ID is used for the URLs that process user interactions for the given `input` step (proceed or abort) and is not correctly encoded.

This allows attackers able to configure Pipelines to have Jenkins build URLs from `input` step IDs that would bypass the CSRF protection of any target URL in Jenkins when the `input` step is interacted with.

Pipeline: Input Step Plugin 456.vd8a_957db_5b_e9 limits the characters that can be used for the ID of `input` steps in Pipelines to alphanumeric characters and URL-safe punctuation. Pipelines with `input` steps having IDs with prohibited characters will fail with an error.

This includes Pipelines that have already been started but not finished before Jenkins is restarted to apply this update.

[Pipeline: Declarative Plugin](https://plugins.jenkins.io/pipeline-model-definition/) provides an `input` directive that is internally using the `input` step, and specifies a non-default ID if not user-defined. Pipeline: Declarative Plugin 2.2114.v2654ca_721309 and earlier may specify values incompatible with this new restriction on legal values: `input` directives in a `stage` use the stage name (which may include prohibited characters) and `input` directives in a `matrix` will use a value generated from the matrix axis values (which always includes prohibited characters). Administrators are advised to update Pipeline: Input Step Plugin and Pipeline: Declarative Plugin at the same time, ideally while no Pipelines are running.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43407
- https://github.com/jenkinsci/pipeline-input-step-plugin/commit/d8a957db5be95ddfbf81f41a60b2f034000314b5
- https://github.com/jenkinsci/pipeline-input-step-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2880
- http://www.openwall.com/lists/oss-security/2022/10/19/3
