# [M] Avo: Direct attachment upload endpoint lacks upload authorization and bypasses field-level upload policy

## Summary
Severity: Medium
Advisory: GHSA-pqpw-cvm4-8mv9
CVE: CVE-2026-53769
CWE: CWE-862, CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-pqpw-cvm4-8mv9
Type: github-advisory

## Affected
- RubyGems: `avo` — affected >=2.28.0 <3.32.0

## Details
### Summary

Avo's direct attachment upload endpoint lacks server-side upload authorization and bypasses the documented field-level upload policy methods such as `upload_{FIELD_ID}?`.

An authenticated Avo user who can reach the Avo attachment upload endpoint can replace or add attachment content, including binary content, filename, and content-type metadata, on a resolved record even when both `update?` and `upload_<field>?` policies deny the operation.

This primarily affects multi-role Avo Pro/Advanced-style deployments where non-administrator or restricted operator users can reach Avo and per-record or per-field operations are expected to be enforced by policies.

### Details

Avo exposes a direct attachment upload endpoint:

```text
POST /<avo-root>/avo_api/resources/:resource_name/:id/attachments/
```

The vulnerable code path is `Avo::AttachmentsController#create`:

- `app/controllers/avo/attachments_controller.rb:9-24`

Current behavior:

```ruby
def create
  blob = ActiveStorage::Blob.create_and_upload! io: params[:file].to_io, filename: params[:filename]
  association_name = BaseResource.valid_attachment_name(@record, params[:attachment_key])

  if association_name
    @record.send(association_name).attach blob
  elsif params[:key].blank?
    raise ActionController::BadRequest.new(...)
  end

  render json: {
    url: main_app.url_for(blob),
    href: main_app.url_for(blob)
  }
end
```

This endpoint creates an `ActiveStorage::Blob` before validating the requested attachment association and before any upload authorization could be enforced. If `attachment_key` resolves to an association, the blob is attached to the target record. If the request uses the key-based/Trix path, the endpoint can still persist the blob and return `url`/`href` even when no attachment association is resolved on the target record.

The controller never calls:

- `@resource.authorization.authorize_action("upload_<field>?", record: @record, ...)`
- `@resource.authorization.authorize_action("update?", record: @record, ...)`

This is inconsistent with the rest of Avo's file authorization implementation. The field-level file authorization concern defines upload authorization as:

- `lib/avo/fields/concerns/file_authorization.rb:11-12`
- `lib/avo/fields/concerns/file_authorization.rb:25-27`

```ruby
def can_upload_file?
  authorize_file_action(:upload)
end

def authorize_file_action(action)
  authorize_action("#{action}_#{id}?", record: record, raise_exception: false)
end
```

That upload policy is used by UI components to decide whether to render upload controls, but the server-side upload endpoint does not enforce the same policy. A user can therefore bypass the policy by directly POSTing to the endpoint.

By contrast, attachment deletion does call attachment-specific authorization:

- `app/controllers/avo/attachments_controller.rb:27-65`

```ruby
def destroy
  if authorized_to :delete
    ...
  end
end

def authorized_to(action)
  @resource.authorization.authorize_action("#{action}_#{params[:attachment_name]}?", record: @record, raise_exception: false)
end
```

The asymmetry is:

- `destroy`: calls `delete_<attachment_name>?`
- `create`: does not call `upload_<attachment_key>?` or `update?`

The field-level upload authorization intent is also documented by Avo:

- Issue #1624 requested the "Ability to police each file upload/download/delete".
  https://github.com/avo-hq/avo/issues/1624
- PR #1625 introduced `upload_cover_photo?` as an example upload policy method.
  https://github.com/avo-hq/avo/pull/1625
- PR #1667 clarified the policy semantics: "From now on, only field level
  authorization will be considered. If it is defined and returns true, the
  action will be granted; otherwise, it will not."
  https://github.com/avo-hq/avo/pull/1667
- The current Avo authorization documentation lists `upload_{FIELD_ID}?` as the
  policy method controlling whether a user can upload an attachment, stating:
  "Controls whether the user can upload the attachment."
  https://docs.avohq.io/4.0/authorization.html
- The same documentation says the same `upload_file?` policy method will be used
  to "authorize the file upload" in action file fields.
  https://docs.avohq.io/4.0/authorization.html

Affected versions observed:

- PoC-confirmed: Avo `3.31.2`, commit
  `46aa6b3bc9e3283110c39e58cfec8bb95adc1897`
- Same vulnerable code path by source inspection: `origin/main` HEAD as of
  2026-05-29,
  `9e23ddc88f2b1e762e4a5ec35a6f86370ac16c73`
- Same vulnerable code path by source inspection: Avo `v4.0.0.beta.26`,
  `6d339595a27f8779cb99b4aa38ddc97cb702b30f`
- Same vulnerable code path by source inspection: `origin/4-dev` at version
  `4.0.0.beta.40`,
  `7ab9794f8b044b11b9677cdc57547d99cf96c3f3`

Suggested affected range for the GitHub Security Advisory form:

```text
>= 2.28.0
```

Rationale:

- The direct attachment upload endpoint exists without upload authorization from
  commit `ab5f5970e2aa76e6ca0a95bf04f510ba7ed5e858` (`feature: trix
  attachments`, 2021-04-24), first included in tag `v1.4.0`.
- The documented field-level upload policy bypass is confirmed from commit
  `667049ceeda838394214489693d088708d9da77d` (`feature: field level file
  authorization`, 2023-03-12), first included in tag `v2.28.0`.
- PR #1667 later clarified the field-level-only grant/deny semantics in commit
  `31b6ef94f8cc4c340a2a75eec36c838cda933ce7`, first included in tag
  `v2.30.1`.

From a narrow missing-authorization perspective, the issue exists from
`v1.4.0`; the `>= 2.28.0` range is a conservative submission range anchored to
the documented field-level upload policy boundary.

Fixed version: to be determined by maintainers.

### PoC

A local request spec was used to reproduce the issue. The PoC adds `pundit` to
the test group and replaces
`Avo::Services::AuthorizationService` with a test double. The test double
records every `authorize_action` invocation and, when invoked, delegates the
decision to a `PostPolicy` resolved via `Pundit.policy!`.

The policy setup is:

- `PostPolicy#update?` returns `false`
- `PostPolicy#upload_attachments?` returns `false`
- `PostPolicy#upload_cover_photo?` returns `false`
- `PostPolicy#method_missing` returns `true` for all other policy methods ending
  in `?`, simulating a user with general read access but explicit update/upload
  denial
- the replacement authorization service records all `authorize_action` calls

The open-source repository does not include Avo Pro's authorization client. The
critical observation is independent of which client is plugged in: the vulnerable
endpoint never invokes `authorize_action` at all, so the call list remains empty.

The PoC user has `roles: {admin: true}`, which is required only to pass the
dummy app's coarse route-level guard:

```ruby
authenticate :user, ->(user) { user.is_admin? }
```

The vulnerability under test is one layer below that guard: the fine-grained
record/field authorization that Avo Pro/Pundit deployments would normally
enforce. The dummy route gate is not part of Avo's upload policy decision. In a
deployment where non-admin operators reach Avo through a different
authentication rule, `AttachmentsController#create` would still skip
`authorize_action` for the upload.

Policy scoping is orthogonal to this finding. Even if `apply_policy` filtered
the record set during lookup, `AttachmentsController#create` would still not
authorize the upload action itself for records that survive the scope.

The spec demonstrates:

1. Normal record update is denied by policy and does not persist changes.
2. Direct upload with `attachment_key=cover_photo` succeeds even though
   `PostPolicy#upload_cover_photo?` returns `false`, replacing the existing
   `has_one_attached` `cover_photo` blob.
3. Direct upload with `attachment_key=attachments` succeeds even though
   `PostPolicy#upload_attachments?` returns `false`, adding to a
   `has_many_attached` association.
4. Direct upload with `params[:key]` and no attachment association succeeds,
   creates an `ActiveStorage::Blob`, and returns `url`/`href` without attaching
   the blob to the record.
5. The direct upload requests do not invoke the replacement authorization
   service at all.

The full request-spec patch can be provided in this advisory thread if useful.

Verification environment:

- Ruby `3.3.1`
- Avo `3.31.2`
- Commit `46aa6b3bc9e3283110c39e58cfec8bb95adc1897`

### Impact

This is a missing server-side authorization vulnerability in Avo's direct
attachment upload endpoint.

The primary affected deployments are Avo Pro/Advanced-style multi-role
deployments where non-administrator or restricted operator users can reach Avo,
and per-record/per-field operations are expected to be enforced by policies.

In such deployments, an authenticated Avo user can add or replace attachment
content on a resolved record even when the host application policy denies both:

- record update, for example `update?`
- field-level upload, for example `upload_cover_photo?` or
  `upload_attachments?`

For `has_one_attached` fields, the demonstrated impact is replacement of a
protected attachment field with attacker-controlled content. The attacker
controls the uploaded binary content, filename, and content-type metadata for
the reachable field.

For key-based/Trix upload flows, the endpoint can persist a blob and return a
URL even when no attachment association is resolved. This means the endpoint
should not be left as an unauthenticated blob creation and URL return path for
authenticated Avo users.

In admin-only deployments following the Avo Community pattern, practical
exposure is much lower because the only users who can reach the endpoint are
already trusted to perform record updates through the normal CRUD path.

Suggested fix direction:

- validate the requested `attachment_key` before any blob is stored
- perform upload authorization before `ActiveStorage::Blob.create_and_upload!`
- derive the policy method from the validated association name rather than raw
  request input
- apply an equivalent authorization decision to supported `params[:key]` / Trix
  upload flows before blob creation or URL return
- return a JSON-compatible `403 Forbidden` response when upload authorization is
  denied

The default `Avo::Services::AuthorizationService#authorize_action` returns
`true` in `lib/avo/services/authorization_service.rb:34-35`, so applications
without a custom authorization client should not see a behavior change from
adding an authorization call. Deployments with custom/Pro authorization clients
that explicitly deny upload would gain enforcement at this endpoint.

No official Avo-level workaround was confirmed in this review. Until a fix is
available, applications can reduce exposure by ensuring only fully trusted
administrators can access Avo routes.

Applications needing an immediate mitigation may override or monkey-patch
`Avo::AttachmentsController#create` to authorize uploads before blob creation.
Any mitigation should be tested against the application's Avo authorization
client and upload UI, because the endpoint is used by Trix/file upload flows.
If a mitigation falls back to `update?` for key-based/Trix uploads, that is a
conservative behavior change for applications that currently allow read-only
operators to use those uploads; those deployments should replace the fallback
with an explicit rich-text upload policy.

## References
- https://github.com/avo-hq/avo/security/advisories/GHSA-pqpw-cvm4-8mv9
- https://github.com/avo-hq/avo
- https://github.com/avo-hq/avo/releases/tag/v3.32.0
