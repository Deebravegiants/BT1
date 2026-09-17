# [M] Craft CMS: Unauthenticated Users Can Perform Restricted Project Config Sync Operations

## Summary
Severity: Medium
Advisory: GHSA-6mrr-q3pj-h53w
CVE: CVE-2026-33159
CWE: CWE-306, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-6mrr-q3pj-h53w
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.14
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.8

## Details
### Summary
Guest users can access Config Sync updater `index`, obtain signed `data`, and execute state-changing Config Sync actions (`regenerate-yaml`, `apply-yaml-changes`) without authentication.

### Details

`ConfigSyncController` extends `BaseUpdaterController`, and the base updater is anonymously accessible for control panel requests.  `index` emits signed updater state (`data`), which can be reused by guests in subsequent requests.

Sensitive actions that are reachable via this method are `actionApplyYamlChanges`, `actionRegenerateYaml`, `applyExternalChanges`, and  `regenerateExternalConfig`.

#### Reproduction steps

1. Guest POST to:

    http POST /admin/actions/config-sync/index

  2. Extract data from returned JS state:

    Craft.updater = ... setState({"data":"<signedData>", ...});

  3. Reuse data as a guest:

```
  POST /admin/actions/config-sync/regenerate-yaml
  data=<signedData>&<csrfParam>=<csrfToken>
```

  or

```
  POST /admin/actions/config-sync/apply-yaml-changes
  data=<signedData>&<csrfParam>=<csrfToken>
```

  4. Observe completed response and state/file changes.

### Impact

Unauthenticated users can execute project configuration sync operations that should be restricted to trusted admin/deployment contexts.

Depending on the pending YAML/config state, this can cause unauthorized config state transitions and a service integrity risk.

### Resources

https://github.com/craftcms/cms/commit/7f0ead833f7

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-6mrr-q3pj-h53w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33159
- https://github.com/craftcms/cms/commit/7f0ead833f7c2b91ae12003caad833479dd08592
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.17.8
- https://github.com/craftcms/cms/releases/tag/5.9.14
