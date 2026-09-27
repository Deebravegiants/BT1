# [C] Label Studio through 1.23.0 Cross-Organization Annotation Access via Unscoped AnnotationAPI Queryset

## Summary
Severity: Critical
Advisory: CVE-2026-76073
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-76073
Type: osv

## Details
Label Studio does not scope the annotation detail endpoint to the requesting user's organization. AnnotationAPI in label_studio/tasks/api.py declares queryset = Annotation.objects.all() and provides no get_queryset override, so the default lookup retrieves any annotation by primary key. The view's permission_required entries name annotations.view, annotations.change and annotations.delete, and label_studio/core/permissions.py registers every permission with rules.is_authenticated, so the check is satisfied by any logged-in account and no object-level organization test runs. The sibling task endpoint does constrain its queryset with project__organization set to the requester's active organization, which is the boundary this path omits. Annotation identifiers are sequential integers, so an authenticated user of one organization can enumerate identifiers to read, modify and delete annotations belonging to other organizations on the same instance. The same unscoped queryset appears on AnnotationConvertAPI in the same file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76073.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76073
- https://www.vulncheck.com/advisories/label-studio-through-cross-organization-annotation-access-via-unscoped-annotationapi-queryset
- https://github.com/HumanSignal/label-studio/issues/9796
- https://github.com/HumanSignal/label-studio
- https://github.com/HumanSignal/label-studio/blob/1.23.0/label_studio/tasks/api.py
