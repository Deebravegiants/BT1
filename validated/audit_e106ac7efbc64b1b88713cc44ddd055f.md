### Title
Webhook Shop-Domain Header Not Covered by HMAC, Enabling Cross-Tenant Webhook Forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from an unauthenticated HTTP header, while the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` relies on to "verify the request did indeed come from Shopify" is computed only over the raw request body. Because the `api_secret_key` is shared across every shop that has installed a given app, a merchant who legitimately installs the app on their own store can capture one authentic `(body, hmac)` pair and replay it to the app's webhook endpoint while forging the `x-shopify-shop-domain` header to name a different (victim) shop. The gem accepts this as authentic and forwards the attacker-chosen `shop` value to the app's handler as trusted tenant identity.

### Finding Description
The signable content for a webhook request is defined as: [1](#0-0) 

This excludes `topic`, `shop-domain`, `webhook_id`, and `api_version` — all of which are pulled straight from attacker-controllable HTTP headers: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then unconditionally trusts `request.shop` to build the tenant context passed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop authenticated == shop bound into HMAC`. In reality: `shop authenticated (header value) != shop covered by HMAC (none, since to_signable_string is body-only)`. The `HmacValidator` itself only checks the signature against the secret, with no knowledge of `shop`: [4](#0-3) 

Because a single `api_secret_key` (the app's `client_secret`) authenticates webhooks for *every* shop that installed the app, `HMAC(body, secret)` is valid for that body regardless of which shop it is claimed to belong to. An attacker who installs the target app on their own shop can trigger a webhook (e.g. `orders/create`) to obtain one genuine `(raw_body, hmac)` pair signed by Shopify, then POST that identical body/HMAC to the app's webhook receiver endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to a different, victim shop that also has the app installed. `HmacValidator.validate` passes (it never inspects `shop`), so `Registry.process` invokes the handler believing the event genuinely originates from the victim shop.

The gem's own documentation reinforces the false guarantee, stating that `Registry.process` "will verify the request did indeed come from Shopify" and describing `data.shop` simply as "The shop domain of the webhook" with no caveat that it is unauthenticated: [5](#0-4) [6](#0-5) 

This directly matches the report's bug class: "a field acted on but not covered by the HMAC" breaks an identity-binding invariant, exactly as in the FLUX report where a balance was mutated (merge) without re-validating the invariant the reward-accrual logic depended on.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce for webhook processing: an attacker with a legitimate (even free/trial) installation on their own store can forge webhook events under an arbitrary shop domain of any other install of the same app, since the shared `client_secret` HMAC never binds to the shop identity. Depending on how the app's handler uses `data.shop` (e.g. as a database lookup key, as in the documented example `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), this allows injection of attacker-controlled data into another tenant's records — a cross-tenant access impact.

### Likelihood Explanation
Any developer following this gem's own documented `Registry.process` usage is affected; no special configuration is required. The only prerequisite is that the attacker has (or creates) an install of the target app on a shop they control — a normal, unprivileged action for any internet user able to install a public/development app — plus knowledge of another shop's domain that also uses the app (often discoverable/guessable, e.g. `*.myshopify.com`).

### Recommendation
Bind the shop identity (and topic/webhook id) into the signed material, or otherwise cryptographically tie the verified HMAC to the claimed shop domain, before treating `request.shop` as authenticated. At minimum, `Registry.process` should require the caller to supply/verify that `request.shop` corresponds to a shop with an active session/installation known to the app, and the gem's documentation should explicitly state that `shop` is unauthenticated header data that must be independently corroborated, rather than describing `process` as verifying that "the request did indeed come from Shopify" for that shop.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (owns `api_secret_key`-signed webhook traffic for their own shop only, as with any legitimate merchant).
2. Attacker triggers an `orders/create` webhook on their own shop and captures the raw POST: body `B` and header `x-shopify-hmac-sha256: H` (valid because `H == HMAC-SHA256(secret, B)`).
3. Attacker resends the identical `B`/`H` to the app's webhook endpoint, replacing `x-shopify-shop-domain: attacker-shop.myshopify.com` with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac` reads `H` from the header, `#to_signable_string` returns `B` (`lib/shopify_api/webhooks/request.rb:36-38`); `HmacValidator.validate` computes `HMAC(B, secret)` and compares to `H` — this matches, so validation succeeds regardless of the spoofed shop header.
5. `Registry.process` calls the handler with `shop: request.shop` equal to `"victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198`), and the app processes/stores attacker-controlled order data under the victim tenant.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
