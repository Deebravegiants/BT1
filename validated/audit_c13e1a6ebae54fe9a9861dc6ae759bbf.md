### Title
Webhook shop identity spoofing — HMAC signs only the raw body, not the `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (used by `Webhooks::Registry.process`) verifies solely that the body bytes are unmodified. The `shop` value that `Registry.process` hands to the app's webhook handler as the trusted tenant identifier is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is never included in the HMAC computation. The binding the gem's own documentation claims to enforce — "this will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`) for the *whole webhook*, including which shop it is for — is broken: `HMAC-valid(raw_body) == HMAC-valid(raw_body)` holds, but `shop-domain header == shop the body actually belongs to` is never checked.

### Finding Description
- `Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 
- `Webhooks::Request#shop` is parsed directly from an attacker-controllable header with no format/tenant validation (unlike `ShopValidator.sanitize!` used elsewhere in the gem): [2](#0-1) 
- `Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. body-only for webhooks) and compares it to the received `hmac`: [3](#0-2) 
- `Registry.process` gates on that body-only HMAC check and then forwards `request.shop` — the unauthenticated header — to the handler as the trusted tenant identity: [4](#0-3) 
- The gem's own docs advertise this call as verifying the request "did indeed come from Shopify," implying the whole webhook (including shop attribution) is authenticated: [5](#0-4) 

Because the header is outside the signed payload, any party who can obtain one genuine `(raw_body, hmac)` pair — trivially done by installing the app on a shop they control and letting Shopify deliver one real webhook — can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value. The HMAC check still passes (it only validates the body), and the handler receives attacker-chosen `data.shop` bound to a body that was never actually generated for that shop.

### Impact Explanation
This breaks the tenant-identity binding the gem is documented to guarantee, letting an unprivileged webhook sender (any user who can install the app on a shop of their own) misattribute a legitimate webhook body to a victim shop of their choosing. Any host application that uses `data.shop` from `WebhookMetadata` to scope tenant-affecting actions (e.g. GDPR data requests, `app/uninstalled` cleanup, order/customer sync keyed by shop) is exposed to cross-tenant confusion/action-on-behalf-of-another-tenant, which maps to the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) obtaining one legitimate webhook body+HMAC pair, achievable by any developer with a free Shopify partner/dev store installing the app, and (2) sending a raw HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header — no access token, `client_secret`, or privileged account is needed. The check is purely mechanical (string comparison over body bytes), so this is reliably reproducible.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the value that is authenticated, or independently verify that the shop in the header corresponds to a shop with an active, stored session/installation before trusting it, rather than passing the raw header value straight to the handler as an authenticated identity.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. `raw_body = '{"id":123}'` with header `x-shopify-hmac-sha256: <valid-hmac-for-raw_body>`.
2. Send a POST to the app's webhook route with the same `raw_body` and same `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only hashes `raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:12-22`).
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed_body, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though this webhook never originated for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
