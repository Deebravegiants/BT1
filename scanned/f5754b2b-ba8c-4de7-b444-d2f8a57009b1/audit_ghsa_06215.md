# [M] OpenWISP IPAM has broken object-level authorization: ExportSubnetView lets a member of one organization export another organization's subnet and all its IP addresses

## Summary
Severity: Medium
Advisory: GHSA-x287-5c68-36wp
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-x287-5c68-36wp
Type: github-advisory

## Affected
- PyPI: `openwisp-ipam` — affected >=0 <1.2.1

## Details
## Summary

OpenWISP IPAM is multi-tenant: every `Subnet` belongs to an `organization`, and API access is scoped to the organizations a user belongs to. The CSV **export** endpoint, `ExportSubnetView`, omits the organization-membership check that its **import** sibling performs, and loads the subnet by primary key with no organization filter. An authenticated user who is a member of one organization can therefore export a subnet belonging to **another** organization — its name, CIDR, organization slug and every IP address in it — by issuing an export request for that subnet's id.

## Details

`ImportSubnetView.post()` authorizes first, by calling `assert_organization_permissions()`:

```python
# openwisp_ipam/api/views.py  (ImportSubnetView)
def post(self, request, *args, **kwargs):
    self.assert_organization_permissions(request)        # <-- org-membership check
    file = request.FILES["csvfile"]
    ...
    self.subnet_model().import_csv(file)
```
```python
# openwisp_ipam/api/utils.py:16  (AuthorizeCSVImport)
def assert_organization_permissions(self, request):
    if request.user.is_superuser:
        return
    # ... otherwise verifies the user belongs to the target organization
```

`ExportSubnetView.post()` performs **no** such check. It is declared with `IpAddressOrgMixin` (whose organization scoping lives in `get_queryset()`), but its overridden `post()` never calls `get_queryset()` **or** `assert_organization_permissions()` — it goes straight to `export_csv()`:

```python
# openwisp_ipam/api/views.py:246
class ExportSubnetView(ProtectedAPIMixin, IpAddressOrgMixin, CreateAPIView):
    subnet_model = Subnet
    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="ip_address.csv"'
        writer = csv.writer(response)
        self.subnet_model().export_csv(kwargs["subnet_id"], writer)   # no org check reached
        return response
```

`export_csv()` resolves the subnet by primary key with no organization filter and writes its full contents:

```python
# openwisp_ipam/base/models.py:242
def export_csv(self, subnet_id, writer):
    ipaddress_model = load_model("openwisp_ipam", "IpAddress")
    subnet = load_model("openwisp_ipam", "Subnet").objects.get(pk=subnet_id)   # any org's subnet
    # ... writes subnet name, CIDR, organization slug, and every IpAddress (address, description, …)
```

The `subnet_id` is a random `UUIDField` (`migrations/0001_initial.py`: `models.UUIDField(default=uuid.uuid4)`), so an attacker must **obtain** the target subnet's id rather than enumerate it — hence **Attack Complexity: High**. This is a genuine missing-authorization flaw regardless: the import/export asymmetry shows the check was intended, and subnet ids routinely appear in URLs, logs, shared CSV exports and support tickets, from which a cross-organization id can leak.

The same single-object pattern (resolving the subnet by `subnet_id` outside the org-scoped queryset) also appears in `AvailableIpView.get()` and `RequestIPView.post()` (the latter additionally **writes** an IP into the target subnet); these are worth reviewing alongside the export fix.

## Proof of concept

Prerequisites: an OpenWISP IPAM instance with two organizations **OrgA** and **OrgB**; a normal (non-superuser) user who is a member of **OrgB** only; a subnet in **OrgA** whose id `S` is known to the attacker (e.g. leaked via a URL/log/shared export).

1. As the OrgB user, authenticate to the API.
2. `POST /api/v1/subnet/{S}/export/` (OrgA's subnet id).
3. **Result:** a CSV download containing OrgA's subnet name, CIDR, organization slug and every IP address in it — even though the user belongs only to OrgB.
4. **Control (proves it's an oversight):** the corresponding import endpoint `POST /api/v1/import-subnet/` with OrgA data is rejected for the same user by `assert_organization_permissions()`.

*(Reported from a first-hand source review of the current `master`: the missing check in `ExportSubnetView.post`, the guarded `ImportSubnetView.post` sibling, the un-filtered `Subnet.objects.get(pk=…)` in `export_csv`, and the `UUIDField` primary key were each verified by hand. The fix is a one-line authorization call, so a maintainer can confirm trivially with two organizations.)*

## Impact

A member of one organization can read the complete contents of another organization's subnet — its IP allocation inventory (addresses, descriptions, organization slug, CIDR). In a WISP / network-management deployment this discloses another tenant's network topology and host inventory. Exploitation requires obtaining the target subnet's UUID (AC:H), but the authorization check is missing outright. (`RequestIPView` shares the pattern and additionally allows writing an IP into another organization's subnet — a separate integrity concern for the maintainer to confirm.)

## Remediation

Add the organization-membership check to `ExportSubnetView.post()` — call `self.assert_organization_permissions(request)` (as `ImportSubnetView` does), or resolve the subnet through the org-scoped `get_queryset()` / `get_object()` and return 404 when it isn't in the caller's organizations. Apply the same to `AvailableIpView` and `RequestIPView`.

## References
- https://github.com/openwisp/openwisp-ipam/security/advisories/GHSA-x287-5c68-36wp
- https://github.com/openwisp/openwisp-ipam/pull/220
- https://github.com/openwisp/openwisp-ipam/commit/04a2ef949498c6591f9ac35713d7451fb9f75362
- https://github.com/openwisp/openwisp-ipam/commit/a4b272461bfa7a1762baf0b1fd76b4f5b681586b
- https://github.com/openwisp/openwisp-ipam
- https://github.com/openwisp/openwisp-ipam/releases/tag/1.2.1
