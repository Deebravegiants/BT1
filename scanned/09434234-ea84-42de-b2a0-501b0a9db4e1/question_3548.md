# Q3548: setup? — rotation window unbounded via rest_disabled

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `rest_disabled` flag, which decides whether the REST client raises at `setup?`, which only checks that four strings are non-empty, makes `Context.setup?` return a result the caller treats as authenticated, given that nothing ever clears `old_api_secret_key`? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup?`
- Entrypoint: `setup?`, which only checks that four strings are non-empty
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: nothing ever clears `old_api_secret_key`
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
