# [M] Decidim: Admin user search allows SQL injection through similarity-based sorting

## Summary
Severity: Medium
Advisory: GHSA-jvqq-cvh4-xm37
CVE: CVE-2026-45376
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-jvqq-cvh4-xm37
Type: github-advisory

## Affected
- RubyGems: `decidim-admin` — affected >=0 <0.30.9
- RubyGems: `decidim-admin` — affected >=0.31.0.rc1 <0.31.5
- RubyGems: `decidim-admin` — affected >=0.32.0.rc1 <0.32.0

## Details
The admin organization user search uses the untrusted term value inside raw SQL ORDER BY expressions. Because the value is interpolated before Rails sanitization is applied, a crafted search string is executed by PostgreSQL as part of the sort expression.

### Technical description
 
The vulnerable endpoint is exposed as GET `/admin/organization/users` in `decidim-admin/config/routes.rb`:

```ruby
resource :organization, only: [:edit, :update], controller: "organization" do
  member do
    get :users
  end
end
```

That route reaches `Decidim::Admin::OrganizationController#users`, which forwards the current organization's available users into `search`:

```ruby
def users
  search(current_organization.users.available)
end
```

Inside `search`, the attacker-controlled source is `params[:term]`:

```ruby
if (term = params[:term].to_s).present?
```

The query has two branches. In both branches, the `WHERE` predicates use bind parameters and are not the injection sink. The vulnerability is in the subsequent `.order(Arel.sql(...))` calls, where the untrusted value is interpolated directly into SQL string literals.

Nickname branch:

```ruby
nickname = term.delete("@")
relation.where("nickname LIKE ?", "#{nickname}%")
  .order(Arel.sql(ActiveRecord::Base.sanitize_sql_array("similarity(nickname, '#{nickname}') DESC")))
```

Name/email branch:

```ruby
relation.where("name ILIKE ?", "%#{term}%").or(
  relation.where("email ILIKE ?", "%#{term}%")
)
  .order(Arel.sql(ActiveRecord::Base.sanitize_sql_array("GREATEST(similarity(name, '#{term}'), similarity(email, '#{term}')) DESC")))
  .order(Arel.sql(ActiveRecord::Base.sanitize_sql_array("(similarity(name, '#{term}') + similarity(email, '#{term}')) / 2 DESC")))
```

This use of `sanitize_sql_array` does not make the code safe. The interpolation happens first, so Rails receives an already-built SQL string rather than a statement with bind placeholders. As a result, a quote in `term` can terminate the intended string literal and inject attacker-controlled SQL into the `ORDER BY` expression.

For example, a payload such as `slpleak '), COALESCE((SELECT 1 FROM pg_sleep(21)),0)) --` produces a fragment equivalent to:

```sql
GREATEST(similarity(name, 'slpleak '), COALESCE((SELECT 1 FROM pg_sleep(21)),0)) --'), similarity(email, 'slpleak '), COALESCE((SELECT 1 FROM pg_sleep(21)),0)) --')) DESC
``` 

The injected subquery is therefore evaluated by PostgreSQL as SQL, not treated purely as data. Because the sink is in `ORDER BY`, the endpoint can still return a normal 200 OK response while exposing the issue through measurable timing differences.

Source-to-sink chain:

* Source: `params[:term]`
* Propagation: `term = params[:term].to_s`
* Sink: `.order(Arel.sql(... "#{term}" ...))` and `.order(Arel.sql(... "#{nickname}" ...))`
* Effect: attacker-controlled SQL is executed inside the database sort expression

Reproduction steps:

1. Authenticate as an organization admin.
2. Ensure the search returns at least one row for the chosen payload. For a deterministic test, create a temporary
user whose `name`, `email`, or `nickname` matches the probe string.
3. Send a control request to `GET /admin/organization/users?term=test` with `Accept: application/json` and record the response time.
4. Send a payload request such as `GET /admin/organization/users?term=slpleak%20%27%29%2C%20COALESCE%28%28SELECT%201%20FROM%20pg_sleep%2821%29%29%2C0%29%29%20--` with `Accept: application/json`.
5. Observe that the endpoint still responds successfully, but the response time increases by approximately the sleep
interval, demonstrating time-based SQL execution in the `ORDER BY` clause.

### Impact

- Exploitation requires an authenticated admin session, which limits exposure but does not remove the underlying SQL injection risk.
- An authenticated admin can inject arbitrary SQL expressions into the query's `ORDER BY` clause and use timing differences as a blind SQL oracle.
- The injection happens inside a database expression, so the effect is not inherently limited to sorting the current organization user relation. Depending on the privileges of the application's PostgreSQL role, an attacker may be able to infer data from other tables readable by that role.
- The issue remains exploitable even without verbose database errors because time-based payloads such as `pg_sleep` provide a reliable blind side channel.
- Repeated long-running payloads can also be used to degrade availability by tying up database-backed requests.

### Patches

See https://github.com/decidim/decidim/pull/16668 

### Workarounds

Review your administrator accesses and not give access to untrustworthy users

### Reference

OWASP SQL Injection

### Credits

This issue was discovered in a security audit organized by the [Decidim Association](https://decidim.org) and made by [Radically Open Security](https://www.radicallyopensecurity.com/) against Decidim financed by [NGI](https://ngi.eu/).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-jvqq-cvh4-xm37
- https://github.com/decidim/decidim/pull/16668
- https://github.com/decidim/decidim
