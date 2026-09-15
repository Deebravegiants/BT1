# [H] Avo: Broken Access Control Through Unauthorized Execution of Arbitrary Action Classes Across Resources

## Summary
Severity: High
Advisory: GHSA-qc5p-3mg5-9fh8
CVE: CVE-2026-42205
CWE: CWE-284, CWE-639
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-qc5p-3mg5-9fh8
Type: github-advisory

## Affected
- RubyGems: `avo` — affected >=0 <3.31.2

## Details
### Summary

A critical Broken Access Control vulnerability was identified in the `ActionsController` of the Avo framework (v3.x). Due to insecure action lookup logic, an authenticated user can execute any Action class (descendants of `Avo::BaseAction`) on any resource, even if the action is not registered for that specific resource. This leads to Privilege Escalation and unauthorized data manipulation across the entire application.

### Details

The vulnerability exists in the `action_class` method within `app/controllers/avo/actions_controller.rb`.

#### Vulnerable Code

```ruby
def action_class
  # It searches through ALL descendants of BaseAction without resource validation
  Avo::BaseAction.descendants.find do |action|
    action.to_s == params[:action_id]
  end
end
```

The controller identifies the action class to execute solely based on the `params[:action_id]` by searching through all `BaseAction` descendants. It fails to verify whether the requested action is actually permitted or registered for the resource context specified in the request URL (e.g., `/admin/resources/posts/actions`).

Consequently, an attacker can invoke sensitive actions (e.g., `Avo::Actions::ToggleAdmin`) through an unrelated resource endpoint (e.g., `Post`), bypassing the intended resource-action mapping.

### Impact

This flaw results in significant security risks:

- **Privilege Escalation:** An authenticated user with low privileges can execute administrative actions (like toggling admin roles) to escalate their own or others' permissions.
- **Unauthorized Operations:** Actions designed for restricted resources can be triggered against any record ID in the database.
- **Data Integrity Compromise:** Attackers can perform unauthorized destructive operations (e.g., Delete, Archive, or Update) on records they should not have access to.

### Proof of Concept (PoC)

**Steps to Reproduce:**

01. Log in to the Avo admin panel with limited permissions.
02. Identify a target record ID (e.g., User ID: 1) and a sensitive action class (e.g., `Avo::Actions::ToggleAdmin`).
03. Send a POST request to a resource endpoint where the target action is not registered:
    - **URL:** `POST /admin/resources/posts/actions`
    - **Payload:** `action_id=Avo::Actions::ToggleAdmin&fields[avo_resource_ids]=1`
04. The server executes the `ToggleAdmin` logic on User 1, even though the request was made through the `posts` resource context.

**PoC Script Snippet:**

```python
# Simulating the unauthorized action execution
data = {
    'action_id': 'Avo::Actions::ToggleAdmin',
    'fields[avo_resource_ids]': '1', # Target Record ID
    'authenticity_token': csrf_token
}
response = session.post(f"{BASE_URL}/admin/resources/posts/actions", data=data)
```

### Remediation

Restrict the action lookup to only those actions explicitly registered for the current resource context:

```ruby
def action_class
  # Validate that the action is registered for the current resource
  @resource.get_actions.find do |action|
    action.to_s == params[:action_id]
  end
end
```

### Discoverer

Illunight

## References
- https://github.com/avo-hq/avo/security/advisories/GHSA-qc5p-3mg5-9fh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-42205
- https://github.com/avo-hq/avo
- https://github.com/avo-hq/avo/releases/tag/v3.31.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/avo/CVE-2026-42205.yml
