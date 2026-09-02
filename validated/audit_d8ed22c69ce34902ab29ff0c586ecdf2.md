Confirmed: `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) only checks `Utils::HmacValidator.validate(request)`, which in turn (`lib/shopify_api/utils/hmac_validator.rb:26-31`) computes the signature over `verifiable_query.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `topic`, `shop`, `api_version`, and `webhook_id` are all read from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:15-33`) and passed straight into `WebhookMetadata` (`lib/shopify_api/webhooks/registry.rb:198-199`) with no cross-check against the signed body.

### Title
Webhook identity headers (`shop`, `topic`, `webhook-id`, `api-version`) are not covered by the HMAC signature, allowing tenant/topic splicing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values consumed by the handler come from HTTP headers that are never included in the signed material, so they carry no cryptographic binding to the body they are shipped with.

### Finding Description
The identity binding the gem is supposed to enforce is:
`hmac == HMAC(secret, bytes_verified)` and `bytes_verified` should equal `bytes_the_app_acts_on`.

In this gem, `bytes_verified` is `@raw_body` only: [1](#0-0) 

But `bytes_the_app_acts_on` additionally includes `shop`, `topic`, `webhook_id`, `api_version`, all parsed from headers outside the signed scope: [2](#0-1) 

`Registry.process` validates only the body-bound HMAC, then trusts these headers to route and tag the payload: [3](#0-2) 

Because Shopify's HMAC only ever signs the body (this is inherent to how Shopify webhooks are delivered, and this gem does nothing to compensate), any two webhook deliveries whose bodies are identical byte-for-byte have interchangeable, still-valid HMACs regardless of which shop, topic, or webhook id header accompanies them. An unprivileged user who operates their own Shopify store (a valid, unprivileged tenant) can capture a `(raw_body, hmac)` pair that Shopify legitimately sent to the app for their own shop/topic, and replay that exact body to the app's public webhook endpoint with a **different** `x-shopify-shop-domain` or `x-shopify-topic` header. `Utils::HmacValidator.validate` still returns `true` because it only ever re-derives the signature from `@raw_body`, and `Registry.process` will dispatch the (attacker-chosen) topic's handler with `WebhookMetadata.shop` set to the attacker-chosen shop domain.

### Impact Explanation
If the host application's webhook handler trusts `WebhookMetadata.shop`/`WebhookMetadata.topic` (as the gem's own documentation and generated `WebhookMetadata` are designed to be trusted post-HMAC-check) to look up or mutate per-tenant state — e.g. treating an `app/uninstalled` or `customers/data_request` or `shop/redact` payload as belonging to a specific merchant, or feeding body fields into a merchant record keyed by the header-derived shop — an attacker who controls only their own store can splice a validly-signed body against a victim shop's identity headers. This crosses a tenant boundary using data nominally "verified" by the gem's HMAC check, which is the class of cross-tenant data-confusion the HMAC is meant to prevent. Because the mandatory compliance topics (`shop/redact`, `customers/redact`, `customers/data_request`) are exactly this kind of trust-sensitive payload, splicing here can misdirect data-erasure/redaction actions to the wrong tenant.

### Likelihood Explanation
Exploitation requires no secret, no token, and no privileged account — only the ability to operate/subscribe an ordinary Shopify store (any developer/merchant account) to capture one legitimate `(body, hmac)` pair, and the ability to POST to the public webhook endpoint the host app exposes (which is, by design, unauthenticated other than the HMAC check). The header values are trivially attacker-controlled in any raw HTTP client. The main mitigating factor is that many host apps additionally validate `shop` against a known/installed-shop list before doing anything sensitive, but the gem itself provides no such binding or warning, and `Registry.process` presents the header-derived `shop`/`topic` as verified once the HMAC check passes.

### Recommendation
Bind the identity headers to the authenticated payload before trusting them: either (a) include `shop`, `topic`, and `webhook_id` in the value hashed/compared for validation (not possible unilaterally since Shopify itself only signs the body — so instead), or (b) explicitly document/enforce that `WebhookMetadata.shop`/`topic` are *not* cryptographically authenticated and must be cross-checked by the host app against its own store of installed shops/expected topics before use, and/or (c) have `Registry.process` reject processing unless the caller supplies (out of band) the expected shop/topic to compare against the header values, so a body replay under a different identity cannot silently succeed.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a `customers/data_request` webhook, capturing the exact `raw_body` and the `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body`/`hmac`, but sets `x-shopify-shop-domain: victim.myshopify.com` and/or `x-shopify-topic: shop/redact`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes `HMAC(secret, raw_body)` and it matches, because the shop/topic headers were never part of the signed material: [4](#0-3) 
4. `Registry.process` dispatches the handler registered for the (attacker-chosen) topic with `WebhookMetadata.shop == "victim.myshopify.com"`, even though Shopify never sent this body for that shop/topic: [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
