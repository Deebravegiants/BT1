# [M] Permissions not properly checked in Invenio-Drafts-Resources

## Summary
Severity: Medium
Advisory: GHSA-xr38-w74q-r8jv
CVE: CVE-2021-43781
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-06
Source: https://github.com/advisories/GHSA-xr38-w74q-r8jv
Type: github-advisory

## Affected
- PyPI: `invenio-drafts-resources` — affected >=0 <0.13.7
- PyPI: `invenio-app-rdm` — affected >=0 <6.0.5
- PyPI: `invenio-rdm-records` — affected >=0 <0.32.6
- PyPI: `invenio-drafts-resources` — affected >=0.14.0 <0.14.6
- PyPI: `invenio-rdm-records` — affected >=0.33.0 <0.33.10
- PyPI: `invenio-app-rdm` — affected >=7.0.0.dev0 <7.0.0.dev5

## Details
### Impact

Invenio-Drafts-Resources does not properly check permissions when a record is published. The vulnerability is exploitable in a default installation of InvenioRDM. An authenticated user is able via REST API calls to publish draft records of other users if they know the record identifier and the draft validates (e.g. all require fields filled out). An attacker is not able to modify the data in the record, and thus e.g. *cannot* change a record from restricted to public.

### Details

The service's ``publish()`` method contains the following permission check:

```python
def publish(..):
    self.require_permission(identity, "publish")
```
However, the record should have been passed into the permission check so that the need generators have access to e.g. the record owner.

```python
def publish(..):
    self.require_permission(identity, "publish", record=record)
```
The bug is activated in Invenio-RDM-Records which has a need generator called ``RecordOwners()``, which when no record is passed in defaults to allow any authenticated user:

```python
class RecordOwners(Generator):
    def needs(self, record=None, **kwargs):
        if record is None:
            return [authenticated_user]
    # ...
```

### Patches

The problem is patched in Invenio-Drafts-Resources v0.13.7 and 0.14.6+, which is part of InvenioRDM v6.0.1 and InvenioRDM v7.0 respectively.

You can verify the version installed of Invenio-Drafts-Resources via PIP:

```console
cd ~/src/my-site
pipenv run pip freeze | grep invenio-drafts-resources
```

### References

- [Security policy](https://invenio.readthedocs.io/en/latest/community/security-policy.html)

### For more information

If you have any questions or comments about this advisory:
* Chat with us on Discord: https://discord.gg/8qatqBC

## References
- https://github.com/inveniosoftware/invenio-drafts-resources/security/advisories/GHSA-xr38-w74q-r8jv
- https://nvd.nist.gov/vuln/detail/CVE-2021-43781
- https://github.com/inveniosoftware/invenio-drafts-resources/commit/039b0cff1ad4b952000f4d8c3a93f347108b6626
- https://github.com/pypa/advisory-database/tree/main/vulns/invenio-app-rdm/PYSEC-2021-837.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/invenio-drafts-resources/PYSEC-2021-836.yaml
