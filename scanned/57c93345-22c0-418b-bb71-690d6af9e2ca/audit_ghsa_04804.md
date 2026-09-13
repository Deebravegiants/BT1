# [H] AlchemyCMS: Unauthenticated nested page API leaks restricted & unpublished content

## Summary
Severity: High
Advisory: GHSA-mqq5-j7w8-2hgh
CWE: CWE-862
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-mqq5-j7w8-2hgh
Type: github-advisory

## Affected
- RubyGems: `alchemy_cms` — affected >=8.2.0 <8.2.6
- RubyGems: `alchemy_cms` — affected >=8.1.0 <8.1.14
- RubyGems: `alchemy_cms` — affected >=8.0.0.a <8.0.15
- RubyGems: `alchemy_cms` — affected >=0 <7.4.15

## Details
# Unauthenticated nested page API leaks restricted & unpublished content

- **Location:** `app/controllers/alchemy/api/pages_controller.rb:28` (`Api::PagesController#nested`)
- **Affected version:** Alchemy CMS 8.3.0.dev (Rails 8.1.3)

## Description

The unauthenticated `GET /api/pages/nested` endpoint returns the full page tree to any anonymous caller, including restricted (member-only) pages and unpublished/draft pages that should be hidden.
Appending `?elements=true` additionally dumps the element/ingredient **content** of restricted pages, fully bypassing the access control the sibling `show` and `index` actions enforce.

## Root cause

`Api::PagesController#nested` calls no `authorize!` and applies no `published`/`restricted` scoping, unlike `show` (`authorize! :show`) and `index` (`accessible_by(current_ability, :index)`).
`PageTreePreloader` loads `page.self_and_descendants` unfiltered, and `PageTreeSerializer` emits every page's metadata (and, with `elements`, `public_version.elements`) with no ability check.

## Evidence

An unauthenticated `GET /api/pages/nested` returns HTTP 200 with the restricted page (`"restricted":true`) and an unpublished draft (`"public":false`); `?elements=true` leaks its content (e.g. `TOPSECRET_RESTRICTED_BODY_proof123`).
The same guest hitting `GET /api/pages/3` (`show`) gets HTTP **403** `{"error":"Not authorized"}`, proving `nested` returns what `show` correctly denies.

### Reproduction

```bash
# 1) Metadata leak (guest, no auth)
curl -s http://localhost:3000/api/pages/nested | python3 -m json.tool | grep -E '"name"|"restricted"|"public"'

# 2) Content leak of restricted page
curl -s "http://localhost:3000/api/pages/nested?elements=true" | grep -oE 'TOPSECRET_RESTRICTED_BODY_[A-Za-z0-9]+|RESTRICTED_RICHTEXT_[A-Za-z0-9]+'

# 3) Contrast — show denies the same guest
curl -s -o /dev/null -w "show /api/pages/3 -> HTTP %{http_code}\n" http://localhost:3000/api/pages/3
```

### Suggested fix

```ruby
def nested
  @page = Page.find_by(id: params[:page_id]) || Language.current_root_page
  authorize! :show, @page
  preloaded_page = PageTreePreloader.new(page: @page, user: current_alchemy_user, ability: current_ability).call
  render json: PageTreeSerializer.new(preloaded_page, ability: current_ability,
                                      user: current_alchemy_user, elements: params[:elements])
end
```

Additionally scope `PageTreePreloader`'s `self_and_descendants` via `accessible_by(current_ability)` and gate element emission in `PageTreeSerializer#page_elements` behind `opts[:ability].can?(:show, page)`.

## References
- https://github.com/AlchemyCMS/alchemy_cms/security/advisories/GHSA-mqq5-j7w8-2hgh
- https://github.com/AlchemyCMS/alchemy_cms
